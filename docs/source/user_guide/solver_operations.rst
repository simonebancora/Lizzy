Running a simulation
====================

In this section we look at various solver operations, including picking a solver and running a filling simulation.
All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods. For more details about the underlying core components, please refer to the :ref:`api_reference_index` documentation.

The solver is a core component of Lizzy, responsible for solving the governing equations that describe flow through porous media. Lizzy uses a finite element / control volume method (FE/CV) to simulate the filling of the part. According to this method, the simulation is discretised into quasi-static time steps. 
At every step, the following operations are carried out:

- the pressure field is computed by solving Darcy's law and continuity equation
- the velocity field is computed from the pressure field using Darcy's law
- a time step is calculated
- the fill state of each control volume at the flow front is updated based on the velocity field and the time step duration

Solver initialization
---------------------

Every Lizzy script is broadly divided in two parts:

- Model definition: the model is created and all elements of the simulation are set. This includes creating mesh, materials, sensors, inlets, etc...
- Solution: the simulation is run and the solution is computed.

The solver initialisation is what separates these two parts. Before it can run the simulation, the solver must always be initialised by calling the :meth:`~lizzy.LizzyModel.initialise_solver` method: 

.. code-block::

    model.initialise_solver()

The solver initialization is a critical point in every Lizzy simulation, because it is the point where a lot of object data types are converted into faster types for performance. As a consequence, several methods do not work anymore after the solver initialisation critical point.

..
   Maybe add an example pictorial illustrated phases here


When we initialise the solver, we can also pick the solver that we want to use. Lizzy currently supports three solvers to compute the pressure solution:

- **Direct dense solver:** uses a direct method to solve the linear system. There is generally no benefit to using this solver, and will be soon discontinued.
- **Direct sparse solver:** uses a direct method and sparse matrix allocation to solve the linear system. This is the default solver in Lizzy if PETSc is not available. Suitable for small to medium-sized problems.
- **Iterative PETSc solver:** uses an iterative method and sparse matrix allocation to solve the linear system. This solver is generally faster and more memory efficient than the direct solvers. This is the default solver in Lizzy if PETSc is available. Users should aim at using this solver if possible. Relies on the PETSc library and the petsc4py package. See the :ref:`installation` page for more details about installing and checking dependencies.

The solver types are available as an Enum :class:`~lizzy.SolverType` in the ``lizzy`` namespace. To pick a solver, we just pass the Enum as an argument to the :meth:`~lizzy.LizzyModel.initialise_solver` method:

.. code-block::

    model.initialise_solver(lizzy.SolverType.ITERATIVE_PETSC)

The :meth:`~lizzy.LizzyModel.initialise_solver` method also accepts other arguments that are specific to certain solvers. Normally, the user does not need to specify any. However, the API reference contains detailed description of all parameters.

Time step vs time interval
--------------------------

Throughout this section, we will encounter multiple times the terms "time step" and "time interval". It is important to clarify the difference between these two concepts:

- **Time step:** The discrete increment of time used by the solver to advance the simulation. The time step is determined by the solver at runtime. **The user has no control over this quantity**.
- **Time interval:** An amount of time over which the simulation advances. A time interval is typically composed of multiple time steps. **The user has full control over this quantity**. For example, if a simulation is run until the part is completely filled, then the time interval is the entird fill time. Conversely, if we set our simulation to run for a fixed time interval, e.g., 60 seconds, then pause and do something, and then resume the simulation, then the time interval is 60 seconds.

Running a simulation until the part is filled
---------------------------------------------

To run the simulation until the part is completely filled, we can call the :meth:`~lizzy.LizzyModel.solve` method:

.. code-block::

    model.solve()

This will start the filling simulation from the latest state (if called for the first time, from the empty part) and keep filling until :attr:`~lizzy.LizzyModel.n_empty_cvs` reaches 0.

.. tip::
    By default, we get a log of the progress:

    .. code-block::

        >>> Fill time: 1001.25s, Empty CVs: 2231
    
    We can suppress that log by passing:

    .. code-block::

        model.solve(log="off")

Running a simulation for a time interval
----------------------------------------

We can run the simulation only for an interval of fill time and then pause by using the method :meth:`~lizzy.LizzyModel.solve_time_interval`. This method needs an argument specifying the duration of the time interval. For example:

.. code-block::

    model.solve_time_interval(300)

will advance the filling simulation for 300 seconds of process time. We can call this method multiple times, and even combine it with :meth:`~lizzy.LizzyModel.solve`:

.. code-block::

    model.initialise_solver()       # the part is empty
    model.solve_time_interval(300)  # fill for 300 seconds
    model.solve_time_interval(600)  # advance filling for another 600 seconds
    model.solve()                   # continue filling until part is filled

Creating dynamic filling scenarios
----------------------------------

The :meth:`~lizzy.LizzyModel.solve_time_interval` method is very powerful when combined to gate management methods like :meth:`~lizzy.LizzyModel.open_inlet` or :meth:`~lizzy.LizzyModel.change_inlet_pressure`. We can create dynamic scenarios, for example:

.. code-block::

    # assume a model that has 2 inlets "inlet_1" and "inlet_2", both open:
    model.initialise_solver()                       # the part is empty
    model.solve_time_interval(600)                  # fill for 600 seconds with both inlets open
    model.close_inlet("inlet_1")                    # close "inlet_1"
    model.solve_time_interval(600)                  # advance filling with only one inlet open
    model.open_inlet("inlet_1")                     # open "inlet_1" again...
    model.change_inlet_pressure("inlet_1", 150000)  # ...and set its pressure to 1.5 bar
    model.solve()                                   # continue filling until part is completely filled

The Solution datatype
---------------------

Lizzy stores solutions using :class:`~lizzy.datatypes.Solution` objects. A Solution object can be seen as a snapshot that stores the current state of the infusion at the time of its creation. When :meth:`~lizzy.LizzyModel.solve` or :meth:`~lizzy.LizzyModel.solve_time_interval` terminate their execution, a Solution object is created. The Solution is returned by the methods, and also stored automatically in the read-only :attr:`~lizzy.LizzyModel.latest_solution` property of the model.

.. tip::

    Two ways to retrieve the current solution:

    - get the latest from the model, after solving: ``solution = model.latest_solution``.

    - catch it from the solving method itself: ``solution = model.solve()`` / ``solution = model.solve_time_interval(100)``.

    Note that, since the same solution object returned is also stored in :attr:`~lizzy.LizzyModel.latest_solution`, usually the manual capture is not necessary (but is given as a possibility for advanced uses).
    
A Solution objects contains all the solution fields computed by the solver, for all time states that were marked for write-out. This is better explained by example:

Let's assume a model is set up, and we specify to save a solution state every 100 seconds of fill time. Then we solve and the simulation completes at 550 seconds of fill time:

.. code-block::

    ...
    model.assign_simulation_parameters(output_interval=100)
    ...
    model.solve()

    >>> Fill time: 550.00s, Empty CVs:    0

At that point, the Solution object will contain results for all these time steps:

- the initial time step (t = 0)
- 5 sequent time intervals every 100 seconds (t=100, t=200, ... , t=500)
- the final time step when the part was filled (t=550)

So in this particular Solution we will have 7 time states. We can get these states by accessing the attributes of the Solution object. For example, let's take a look at the shape of the time, pressure and velocity field:

.. code-block::

    solution = model.latest_solution
    print(f"Number of time states stored: {solution.n_time_states}")
    print(f"Time field shape: {solution.time.shape}")
    print(f"Pressure field shape: {solution.p.shape}")
    print(f"Velocity field shape: {solution.v.shape}")

    >>> Number of time states stored: 7
        Time field shape: (7,)
        Pressure field shape: (7, 735)
        Velocity field shape: (7, 1366, 3)
    
    # Let's print the content of solution.time to see the values:
    print(solution.time)

    >>> [  0. 100. 200. 300. 400. 500. 550.]

Each field that is stored in the Solution has a leading dimension equal to the number of time states present in the Solution. So for example, if we want the pressure field at t=200s (third time state), we can type: ``solution.p[2]``.
Consult the :class:`~lizzy.datatypes.Solution` API reference to get more information on the fields stored.

The Solution object is also used by Lizzy to write result files. More information on this in :ref:`saving_results`.

Resetting a simulation
----------------------

To reset the simulation and run it again from scratch — without rebuilding the model — use the :meth:`~lizzy.LizzyModel.initialise_new_solution` method:

.. code-block::

    model.initialise_new_solution()

This empties the part, resets the simulation time to zero, restores all inlets to their initial open/closed state, and clears all sensor readings. The mesh, materials, boundary conditions, and preprocessed data (stiffness matrix, etc.) are preserved, making this faster than calling :meth:`~lizzy.LizzyModel.initialise_solver` again.

This can be useful for parametric studies, where the same mesh and material setup is reused across multiple runs.

.. note::
    The methods :meth:`~lizzy.LizzyModel.initialise_new_solution` and :meth:`~lizzy.LizzyModel.initialise_solver` are different. The former merely resets the simulation fields and gate states to initial values, but does not initialise the solver anew. Any method that requires being called before solver initialisation will still need to reinitialise the solver with :meth:`~lizzy.LizzyModel.initialise_solver`. On the other hand, :meth:`~lizzy.LizzyModel.initialise_solver` also calles :meth:`~lizzy.LizzyModel.initialise_new_solution` internally.


