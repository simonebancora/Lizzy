===========
Using Lizzy
===========

In this section, we detail how to use Lizzy setting up and running simulations. The philosophy of Lizzy is inspired to popular FE libraries like `FEniCS <https://fenicsproject.org>`_: we provide a flexible scripting API that allows the user to define any type of infusion scenario. Everything in Lizzy is accomplished by writing a Python script.


Basic script workflow
----------------------

The basic workflow for writing a Python script to use Lizzy involves the following key steps:

1. Import the Lizzy package.
2. Instantiate a :class:`~lizzy.LizzyModel` object.
3. Use the :class:`~lizzy.LizzyModel` API to define and run the simulation.
4. Save results.

Lizzy is designed so that most of the operations are performed using the :class:`~lizzy.LizzyModel` class directly.

Units and conventions
----------------------
The solver assumes consistent units and does not enforce any. The user is free to use any system of units, as long as they are consistent throughout the script. We recommend to stick to the SI units:

- Permeability: m²
- Viscosity: Pa·s
- Length: m
- Time: s
- Pressure: Pa
- Velocity: m/s

Time step vs time interval
--------------------------

Throughout this documentation, we will encounter multiple times the terms "time step" and "time interval". It is important to clarify the difference between these two concepts:

- Time step: the discrete increment of time used by the solver to advance the simulation. The time step is determined by the solver at runtime and **the user has no control over this quantity**.
- Time interval: an amount of time over which the simulation advances. A time interval is tipically composed of multiple time steps. **The user has full control over this quantity**. For example, if a simulation is run until the part is completely filled, then the time interval is the entird fill time. Conversely, we can set our simulation to run for a fixed time interval, e.g., 60 seconds, then pause and do something, and then resume the simulation for another time interval... and so on.

The LizzyModel class
---------------------

The :class:`~lizzy.LizzyModel` class is the main protagonist of any Lizzy script. This class provides APIs to execute all the core fucntionalities of the solver.
When writing a Lizzy script, typically the first step (after importing the library) is to instantiate a :class:`~lizzy.LizzyModel` object:

.. code-block::

    model = liz.LizzyModel()

The Lizzy API is designed so that, in most cases, the :class:`~lizzy.LizzyModel` class is the only one the user needs do access to do any operation:

.. code-block::

    operation_output = model.some_method(args)


In this section, we cover the most common operations that can be performed using a LizzyModel object.

.. toctree::
   :maxdepth: 1

   reading_a_mesh
   assigning_parameters
   managing_materials
   assigning_boundary_conditions

.. seealso::

    :ref:`tutorials`
         A collection of tutorials to learn the LizzyModel API.

    :ref:`LizzyModel API reference <lizzymodel_api>`
        The API reference of the LizzyModel class.

See also
^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   components/inlet_operations