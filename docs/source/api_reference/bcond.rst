.. py:currentmodule:: lizzy.bcond

lizzy.bcond
===========

.. autoclass:: lizzy.bcond.bcond.BCManager

    Properties
    ----------
    
    .. autoproperty:: BCManager.existing_inlets
    .. autoproperty:: BCManager.assigned_inlets

    Methods
    -------

    .. rubric:: Inlet management methods

    .. automethod:: BCManager.create_inlet
    .. automethod:: BCManager.assign_inlet
    .. automethod:: BCManager.reset_inlets
    
    .. rubric:: Inlet control methods
    .. automethod:: BCManager.change_inlet_pressure
    .. automethod:: BCManager.open_inlet
    .. automethod:: BCManager.close_inlet
    

.. autoclass:: lizzy.bcond.bcond.Inlet
    :members:
    :undoc-members: