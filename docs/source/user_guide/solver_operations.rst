Running a simulation
====================

In this section we look at various solver operations, including picking a solver, running a filling simulation and saving results.
All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods. For more details about the underlying core components, please refer to the :ref:`api_reference_index` documentation.

The solver is a core component of Lizzy, responsible for solving the governing equations that describe flow through porous media. Lizzy uses a finite element / control volume method (FE/CV) to simulate the filling of the part. According to this method, the simulation is discretised into quasi-static time steps. 
At every step, the following operations are carried out:

- the pressure field is computed by solving Darcy's law and continuity equation
- the velocity field is computed from the pressure field using Darcy's law
- a time step is calculated
- the fill state of each control volume at the flow front is updated based on the velocity field and the time step duration

Currently, Lizzy supports three solvers to compute the pressure solution:

- **Direct dense solver:** uses a direct method to solve the linear system. There is generally no benefit to using this solver, and will be soon discontinued.
- **Direct sparse solver:** uses a direct method and sparse matrix allocation to solve the linear system. This is the default solver in Lizzy if PETSc is not available. Suitable for small to medium-sized problems.
- **Iterative PETSc solver:** uses an iterative method and sparse matrix allocation to solve the linear system. This solver is generally faster and more memory efficient than the direct solvers. This is the default solver in Lizzy if PETSc is available. Users should aim at using this solver if possible. Relies on the PETSc library and the petsc4py package. See the :ref:`installation` page for more details about installing and checking dependencies.

Time step vs time interval
--------------------------

Throughout this section, we will encounter multiple times the terms "time step" and "time interval". It is important to clarify the difference between these two concepts:

- **Time step:**
    The discrete increment of time used by the solver to advance the simulation. The time step is determined by the solver at runtime and **the user has no control over this quantity**.
- **Time interval:**
    An amount of time over which the simulation advances. A time interval is tipically composed of multiple time steps. **The user has full control over this quantity**. For example, if a simulation is run until the part is completely filled, then the time interval is the entird fill time. Conversely, we can set our simulation to run for a fixed time interval, e.g., 60 seconds, then pause and do something, and then resume the simulation for another time interval... and so on.