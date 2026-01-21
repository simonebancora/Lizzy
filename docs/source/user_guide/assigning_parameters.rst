Simulation Parameters
=========================

When simulating an infusion using Lizzy, there are some process and simulation parameters which are assigned globally in the model. These are notably the fluid viscosity, the frequency of solution write-outs and more.
These parameters are stored in a :class:`~lizzy.datatypes.SimulationParameters` data class.
The parameters that are stored in the class are the following:

- :attr:`~lizzy.datatypes.SimulationParameters.mu`: Fluid viscosity [Pa s]. Default: 0.1. Currently, Lizzy only supports a constant viscosity value.
- :attr:`~lizzy.datatypes.SimulationParameters.wo_delta_time`: The interval of simulation time between solution write-outs [s] if no other conditions trigger a write-out. Default: -1 (write-out every numerical time step, usually undesired)
- :attr:`~lizzy.datatypes.SimulationParameters.fill_tolerance`: Tolerance on the fill factor to consider a CV as filled. Default: 0.01 (a CV is considered filled when its fill factor is >= 0.99).
- :attr:`~lizzy.datatypes.SimulationParameters.end_step_when_sensor_triggered`: If True, whenever a sensor is reached for the first time by the fluid, the current solution step is ended and a write-out is created. Default: False

Assigning simulation parameters
--------------------------------

The following operations are to be performed **before** the solver is initialised by calling :meth:`~lizzy.LizzyModel.initialise_solver`.

Each simulation parameter can be assigned to the model by keyword, using the :meth:`~lizzy.LizzyModel.assign_simulation_parameters` method:

.. code-block::

    model.assign_simulation_parameters(mu=0.1, wo_delta_time=100)

In this example, we have assigned a fluid viscosity value of 0.1 Pa.s and we have told the solver to save a solution state every 100 seconds of simulation time.

To print the currently assigned simulation parameters to the console, we can use the :meth:`~lizzy.LizzyModel.print_simulation_parameters` method:

.. code-block::

    >>> model.print_simulation_parameters()

    >>> Currently assigned simulation parameters:
        - "mu": 0.1 [Pa s],
        - "wo_delta_time": 100 [s],
        - "fill_tolerance": 0.01,
        - "end_step_when_sensor_triggered": False,

