.. py:currentmodule:: lizzy.core.sensors

lizzy.core.sensors
==================

The SENSORS module contains the :class:`~lizzy.core.sensors.SensorManager` class, which is responsible for managing all sensors in the model. The :class:`~lizzy.core.sensors.SensorManager` is instantiated by the constructor of the :class:`~lizzy.lizmodel.LizzyModel`, and belongs to the model.

.. autoclass:: lizzy.core.sensors.SensorManager

    .. rubric:: Methods

    .. automethod:: SensorManager.add_sensor
    .. automethod:: SensorManager.reset_sensors
    .. automethod:: SensorManager.print_sensor_readings
    .. automethod:: SensorManager.get_sensor_by_id

.. autoclass:: lizzy.core.sensors.Sensor

    .. rubric:: Properties

    .. autoproperty:: Sensor.idx
    .. autoproperty:: Sensor.position
    .. autoproperty:: Sensor.pressure
    .. autoproperty:: Sensor.velocity
    .. autoproperty:: Sensor.fill_factor
    .. autoproperty:: Sensor.time

    .. rubric:: Methods

    .. automethod:: Sensor.info