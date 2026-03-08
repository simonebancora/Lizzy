.. py:currentmodule:: lizzy

.. _lizzymodel_api:

======
lizzy
======

The LIZZY namespace exposes the :class:`~lizzy.LizzyModel` class, which provides all the user-facing APIs to interact with Lizzy. It also exposes the :class:`~lizzy.SolverType` enum, which contains the available solver types to choose from.

.. autoclass:: lizzy.LizzyModel

    Properties
    ----------
    
    .. autoproperty:: lizzy.LizzyModel.lightweight
    .. autoproperty:: lizzy.LizzyModel.assigned_materials
    .. autoproperty:: lizzy.LizzyModel.existing_materials
    .. autoproperty:: lizzy.LizzyModel.n_empty_cvs
    .. autoproperty:: lizzy.LizzyModel.current_time
    .. autoproperty:: lizzy.LizzyModel.latest_solution

    Model setup methods
    -------------------

    .. automethod:: lizzy.LizzyModel.read_mesh_file
    .. automethod:: lizzy.LizzyModel.print_mesh_info
    .. automethod:: lizzy.LizzyModel.create_material
    .. automethod:: lizzy.LizzyModel.assign_material
    .. automethod:: lizzy.LizzyModel.assign_simulation_parameters
    .. automethod:: lizzy.LizzyModel.print_simulation_parameters

    
    Inlet management methods
    ------------------------
    
    .. automethod:: lizzy.LizzyModel.create_pressure_inlet
    .. automethod:: lizzy.LizzyModel.create_flowrate_inlet

    .. automethod:: lizzy.LizzyModel.assign_inlet
    .. automethod:: lizzy.LizzyModel.fetch_inlet_by_name
    .. automethod:: lizzy.LizzyModel.change_inlet_pressure
    .. automethod:: lizzy.LizzyModel.open_inlet
    .. automethod:: lizzy.LizzyModel.close_inlet
    
    Vent management methods
    -----------------------

    .. automethod:: lizzy.LizzyModel.create_vent
    .. automethod:: lizzy.LizzyModel.assign_vent

    Sensor management methods
    -------------------------
    
    .. automethod:: lizzy.LizzyModel.create_sensor
    .. automethod:: lizzy.LizzyModel.print_sensor_readings
    .. automethod:: lizzy.LizzyModel.get_sensor_trigger_states
    .. automethod:: lizzy.LizzyModel.get_sensor_by_id

    Solver methods
    --------------
    
    .. automethod:: lizzy.LizzyModel.initialise_solver
    .. automethod:: lizzy.LizzyModel.solve
    .. automethod:: lizzy.LizzyModel.solve_time_interval
    .. automethod:: lizzy.LizzyModel.initialise_new_solution
    .. automethod:: lizzy.LizzyModel.save_results
    


.. autoclass:: lizzy.SolverType
    :members:
    :member-order: bysource
    :undoc-members:
    :show-inheritance:

