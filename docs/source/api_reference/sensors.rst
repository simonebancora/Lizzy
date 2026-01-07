.. py:currentmodule:: lizzy.core.sensors

lizzy.core.sensors
==================

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


.. autoclass:: lizzy.core.sensors.SensorManager

    .. rubric:: Methods

    .. automethod:: SensorManager.add_sensor
    .. automethod:: SensorManager.reset_sensors
    .. automethod:: SensorManager.print_sensor_readings
    .. automethod:: SensorManager.get_sensor_by_id
