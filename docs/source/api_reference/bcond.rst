.. py:currentmodule:: lizzy.core.bcond

lizzy.core.bcond
================

The BCOND module provides functionality related to all boundary condition operations. The most important component is the :class:`~lizzy.core.bcond.BCManager` class, which is responsible for managing all boundary conditions. The :class:`~lizzy.core.bcond.BCManager` is instantiated by the constructor of the :class:`~lizzy.lizmodel.lizmodel.LizzyModel`, and belongs to the model.

.. autoclass:: lizzy.core.bcond.BCManager

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
    

.. autoclass:: lizzy.core.bcond.Inlet
    
    .. rubric:: Properties

    .. autoproperty:: Inlet.p_value
    .. autoproperty:: Inlet.p0
    .. autoproperty:: Inlet.is_open
    
    .. rubric:: Methods

    .. automethod:: Inlet.reset
    .. automethod:: Inlet.set_open