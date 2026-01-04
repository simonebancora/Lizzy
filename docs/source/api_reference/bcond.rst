.. py:currentmodule:: lizzy.bcond

lizzy.bcond
===========

.. autoclass:: lizzy.bcond.bcond.BCManager

    .. rubric:: Properties
    
    .. autoproperty:: BCManager.existing_inlets
    .. autoproperty:: BCManager.assigned_inlets

    .. rubric:: Methods

    .. automethod:: BCManager.create_inlet
    .. automethod:: BCManager.assign_inlet
    .. automethod:: BCManager.reset_inlets
    .. automethod:: BCManager.change_inlet_pressure
    .. automethod:: BCManager.open_inlet
    .. automethod:: BCManager.close_inlet
    

.. autoclass:: lizzy.bcond.bcond.Inlet
    
    .. rubric:: Properties

    .. autoproperty:: Inlet.p_value
    .. autoproperty:: Inlet.p0
    .. autoproperty:: Inlet.is_open
    
    .. rubric:: Methods

    .. automethod:: Inlet.reset
    .. automethod:: Inlet.set_open