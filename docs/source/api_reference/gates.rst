.. py:currentmodule:: lizzy.gates

lizzy.gates
===========


.. autoclass:: lizzy.gates.Inlet

    .. rubric:: Properties

    .. autoproperty:: Inlet.name
    .. autoproperty:: Inlet.is_open
    .. autoproperty:: Inlet.type

    .. rubric:: Methods

    .. automethod:: Inlet.reset
    .. automethod:: Inlet.set_open

.. autoclass:: lizzy.gates.PressureInlet

    .. rubric:: Properties

    .. autoproperty:: PressureInlet.p_value
    .. autoproperty:: PressureInlet.p0
    .. autoproperty:: PressureInlet.is_open

    .. rubric:: Methods

    .. automethod:: PressureInlet.reset
    .. automethod:: PressureInlet.set_open

.. autoclass:: lizzy.gates.FlowRateInlet

    .. rubric:: Properties

    .. autoproperty:: FlowRateInlet.q_value
    .. autoproperty:: FlowRateInlet.q0
    .. autoproperty:: FlowRateInlet.is_open

    .. rubric:: Methods

    .. automethod:: FlowRateInlet.reset
    .. automethod:: FlowRateInlet.set_open

.. autoclass:: lizzy.gates.Vent

    .. rubric:: Properties

    .. autoproperty:: Vent.vacuum_pressure
