.. py:currentmodule:: lizzy.sensors

lizzy.sensors
=============

.. autoclass:: lizzy.sensors.sensmanager.Sensor

    Properties
    ----------

    .. autoproperty:: Sensor.idx
    .. autoproperty:: Sensor.position
    .. autoproperty:: Sensor.pressure
    .. autoproperty:: Sensor.velocity
    .. autoproperty:: Sensor.fill_factor
    .. autoproperty:: Sensor.time

    Methods
    -------

    .. automethod:: Sensor.info


.. autoclass:: lizzy.sensors.sensmanager.SensorManager

    Methods
    -------

    .. automethod:: SensorManager.add_sensor
    .. automethod:: SensorManager.reset_sensors
    .. automethod:: SensorManager.print_sensor_readings
    .. automethod:: SensorManager.get_sensor_by_id
