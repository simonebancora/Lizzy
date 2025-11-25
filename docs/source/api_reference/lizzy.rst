.. py:currentmodule:: lizzy

.. _lizzymodel_api:

======
lizzy
======

.. autoclass:: lizzy.LizzyModel

    Properties
    ----------
    
    .. autoproperty:: lizzy.LizzyModel.lightweight
    .. autoproperty:: lizzy.LizzyModel.assigned_materials
    .. autoproperty:: lizzy.LizzyModel.existing_materials
    .. autoproperty:: lizzy.LizzyModel.n_empty_cvs
    .. autoproperty:: lizzy.LizzyModel.current_time
    .. autoproperty:: lizzy.LizzyModel.latest_solution

    Methods
    -------
    
    .. rubric:: Inlet management methods
    
    .. automethod:: lizzy.LizzyModel.create_inlet
    .. automethod:: lizzy.LizzyModel.assign_inlet
    .. automethod:: lizzy.LizzyModel.change_inlet_pressure
    .. automethod:: lizzy.LizzyModel.open_inlet
    .. automethod:: lizzy.LizzyModel.close_inlet

    .. rubric:: Sensor management methods
    
    .. automethod:: lizzy.LizzyModel.create_sensor
    .. automethod:: lizzy.LizzyModel.print_sensor_readings
    .. automethod:: lizzy.LizzyModel.get_sensor_trigger_states
    .. automethod:: lizzy.LizzyModel.get_sensor_by_id
    
    .. rubric:: Getter methods

    .. automethod:: lizzy.LizzyModel.get_number_of_empty_cvs
    .. automethod:: lizzy.LizzyModel.get_current_time
    .. automethod:: lizzy.LizzyModel.get_latest_solution
    
    .. rubric:: Core model setup methods
    .. automethod:: lizzy.LizzyModel.read_mesh_file
    .. automethod:: lizzy.LizzyModel.create_material
    .. automethod:: lizzy.LizzyModel.assign_material
    .. automethod:: lizzy.LizzyModel.assign_simulation_parameters

    .. rubric:: Solver methods
    
    .. automethod:: lizzy.LizzyModel.initialise_solver
    .. automethod:: lizzy.LizzyModel.solve
    .. automethod:: lizzy.LizzyModel.solve_step
    .. automethod:: lizzy.LizzyModel.initialise_new_solution
    .. automethod:: lizzy.LizzyModel.save_results
    


.. autoclass:: lizzy.SolverType
    :members:
    :member-order: bysource
    :undoc-members:
    :show-inheritance:

.. autoclass:: lizzy.Rosette
    :members:
    :member-order: bysource
    :undoc-members:
    :show-inheritance: