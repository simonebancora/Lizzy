.. _using_sensors:

Using sensors
=============

In this section we describe how to create and use virtual sensors in Lizzy. All operations can be performed using the :class:`~lizzy.LizzyModel` user-facing methods.

Sensors in Lizzy
-----------------

In Lizzy, a virtual sensor is represented by the :class:`~lizzy.sensors.Sensor` class. A sensor is a point probe placed at a specific location in the domain. During the simulation, Lizzy records the local values of pressure, velocity, and fill factor at the sensor location at each time step, making them available for reading at runtime or post-processing.


Creating sensors
-----------------

.. note::
    The following operations are to be performed **before** the solver is initialised by calling :meth:`~lizzy.LizzyModel.initialise_solver`.

To create a sensor, use the :meth:`~lizzy.LizzyModel.create_sensor` method, providing an name for the sensor and the (x, y, z) coordinates of the position where it will be placed. For example, to place a sensor called "sensor_01" at position (0.5, 0.5, 0.0):

.. code-block::

    model.create_sensor("sensor_01", (0.5, 0.5, 0.0))

You can create as many sensors as needed.


Fetching sensors from the model
---------------------------------

To retrieve a sensor object from the model, use the :meth:`~lizzy.LizzyModel.get_sensor_by_name` method, providing the sensor's name:

.. code-block::

    sensor = model.get_sensor_by_name("sensor_01")

This returns the :class:`~lizzy.sensors.Sensor` object with that name.

.. note::
    This method can be called both before and after the solver has been initialised.

Reading sensor data at runtime
--------------------------------

Sensor data is only available **after** the solver has been initialised by calling :meth:`~lizzy.LizzyModel.initialise_solver`.
The solver stores filed values at created sensors at the end of each write-out time period (specified in the :ref:`simulation parameters <assigning_parameters>`). The following read-only properties are available in a :class:`~lizzy.sensors.Sensor` object:

- :attr:`~lizzy.sensors.Sensor.name`: the name of the sensor.
- :attr:`~lizzy.sensors.Sensor.position`: the (x, y, z) coordinates of the sensor.
- :attr:`~lizzy.sensors.Sensor.pressure`: the current resin pressure (Pa) at the sensor location.
- :attr:`~lizzy.sensors.Sensor.velocity`: the current resin velocity (m/s) at the sensor location.
- :attr:`~lizzy.sensors.Sensor.fill_factor`: the current fill factor at the sensor location (0 = empty, 1 = fully filled).
- :attr:`~lizzy.sensors.Sensor.time`: the current simulation time (s).
- :attr:`~lizzy.sensors.Sensor.resin_arrived`: boolean that is ``True`` if the resin front has reached the sensor location.
- :attr:`~lizzy.sensors.Sensor.trigger_time`: the time at which the sensor was triggered by the resin arrival.

For example, after advancing the simulation, we can read the sensor values as follows:

.. code-block::

    model.solve_time_interval(300)
    sensor = model.get_sensor_by_name("sensor_01")
    print(sensor.time)
    print(sensor.pressure)
    print(sensor.fill_factor)

.. code-block:: console

    >>> 300.0
    >>> 87432.5
    >>> 0.73

To print a summary of all sensor readings at a given instant, use the :meth:`~lizzy.LizzyModel.print_sensor_readings` method:

.. code-block::

    model.print_sensor_readings()

.. code-block:: console

    >>> {0: 'time: 300.0 s; resin pressure: 87432.5 Pa; fill factor: 1.0, resin velocity: [0.00012 0. 0.] m/s, resin arrived: True, trigger time: 160.0 s',
         1: 'time: 300.0 s; resin pressure: 54210.1 Pa; fill factor: 1.0, resin velocity: [0.00009 0. 0.] m/s, resin arrived: True, trigger time: 250.0 s'}

Resin arrival detection
------------------------

Each sensor has a :attr:`~lizzy.sensors.Sensor.resin_arrived` boolean attribute that becomes ``True`` as soon as the fill factor at the sensor location reaches or exceeds 0.5, and a :attr:`~lizzy.sensors.Sensor.trigger_time` attribute that records the time at which the arrival happened. For example:

.. code-block::

    sensor = model.get_sensor_by_name("sensor_01")
    if sensor.resin_arrived:
        print(f"Resin has reached this sensor at time= {sensor.trigger_time} s")

To get the trigger state of all sensors at once as a list of booleans, use the :meth:`~lizzy.LizzyModel.get_sensor_trigger_states` method:

.. code-block::

    states = model.get_sensor_trigger_states()
    print(states)

.. code-block:: console

    >>> [True, True, False]

In this example, the first 2 sensors have been reached by resin, the third one hasn't.

Triggering write-outs on sensor events
----------------------------------------

By enabling the ``end_step_when_sensor_triggered`` simulation parameter, Lizzy will automatically end the current solution step and create a result write-out whenever a sensor transitions to the triggered state (i.e., when the resin front reaches a sensor for the first time). This ensures that the exact moment of resin arrival is always captured in the solution, independently of the regular write-out schedule (``output_interval``).

To enable this behaviour, set the parameter before initialising the solver:

.. code-block::

    model.set_simulation_parameters(end_step_when_sensor_triggered=True)

See :ref:`assigning_parameters` for more details on simulation parameters.

Building dynamic scenarios with sensors
-----------------------------------------

Sensors become useful when combined with the :meth:`~lizzy.LizzyModel.solve_time_interval` method to create dynamic filling scenarios. For example, we can advance the simulation in short intervals, check the sensor state after each interval, and react accordingly:

.. tip::

    The following example shows how to close an inlet as soon as the resin reaches a sensor, simulating a sequential infusion strategy:

    .. code-block::

        model.set_simulation_parameters(end_step_when_sensor_triggered=True)
        model.initialise_solver()

        # Fill until resin reaches sensor 01 (located at the mid-point of the part)
        while not model.get_sensor_by_name("sensor_01").resin_arrived:
            model.solve_time_interval(10)

        # Resin has arrived at sensor 01: close inlet_1 and open inlet_2
        model.close_inlet("inlet_1")
        model.open_inlet("inlet_2")

        # Continue filling until the part is completely filled
        model.solve()

.. seealso::

    :ref:`assigning_boundary_conditions`
        Opening, closing and modifying inlets at runtime.

    :class:`~lizzy.sensors.Sensor` API reference
        Full list of properties and methods available on the Sensor class.
