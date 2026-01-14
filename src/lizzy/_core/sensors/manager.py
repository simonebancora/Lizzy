#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.cvmesh.mesh import Mesh
    from lizzy._core.sensors.sensor import Sensor
    
import numpy as np



class SensorManager:
    """Manager for all sensor operations.
    """
    def __init__(self):
        #TODO: these need to become properties...
        self.sensors : list[Sensor] = []
        self.sensors_dict = {}
        self.sensor_trigger_states = []

    def add_sensor(self, x:float, y:float, z:float):
        """Creates a new :class:`~lizzy.sensors.sensmanager.Sensor` at the specified location and registers it in the sensor manager.

        Parameters
        ----------
        x : float
            x coordinate of the sensor.
        y : float
            y coordinate of the sensor.
        z : float
            z coordinate of the sensor.
        """
        new_sensor = Sensor(x, y, z)
        idx = len(self.sensors)
        new_sensor._idx = idx
        self.sensors.append(new_sensor)
        self.sensors_dict[idx] = new_sensor
    
    def initialise(self, mesh:Mesh):
        """Perform some precalculations to initialise the manager. This method is called automatically by the solver when a new simulation is initialised (not meant for user).
        """
        if len(self.sensors) > 0:
            all_node_coords = mesh.nodes.XYZ
            for sensor in self.sensors:
                distances = []
                for node_coords in all_node_coords:
                    distances.append(np.linalg.norm(sensor.position - node_coords))
                id_closest_node = np.argmin(np.array(distances))
                sensor.child_node = mesh.nodes[id_closest_node]
            self.sensor_trigger_states = np.array([False for s in self.sensors])
    
    def probe_current_solution(self, p_array, v_array, f_array, current_time):
        """This method updates the existing sensors with the current solution values. This method is called automatically by the solver (not meant for user)."""
        if len(self.sensors) > 0:
            for sensor in self.sensors:
                sensor._tvals.append(current_time)
                sensor._pvals.append(p_array[sensor.child_node.idx])
                sensor._fvals.append(f_array[sensor.child_node.idx])
                sensor._vvals.append(v_array[sensor.child_node.idx])
                if sensor.fill_factor >= 0.5:
                    sensor.resin_arrived = True

    def reset_sensors(self):
        """Resets all sensors to their initial state.
        """
        if len(self.sensors) > 0:
            for sensor in self.sensors:
                sensor._reset()
        self.sensor_trigger_states = np.array([False for s in self.sensors])

    def check_for_new_sensor_triggered(self, fill_factor_array) -> bool:
        """Runs through all sensors and updates their :attr:`~lizzy.sensors.sensmanager.Sensor.resin_arrived` attribute based on the current fill factor. Then checks if any new sensor has been triggered compared to the previously recorded state. If so, returns True. This method is called automatically by the solver if needed (not meant for user).
        """
        triggered = False
        for sensor in self.sensors:
            if fill_factor_array[sensor.child_node.idx] >= 0.5:
                sensor.resin_arrived = True
        current_trigger_states = np.array([sensor.resin_arrived for sensor in self.sensors])
        diff = current_trigger_states != self.sensor_trigger_states
        if np.any(diff):
            self.sensor_trigger_states = current_trigger_states
            triggered = True
        return triggered

    def print_sensor_readings(self):
        """Prints to the console the current values of :attr:`~lizzy.sensors.sensmanager.Sensor.time`, :attr:`~lizzy.sensors.sensmanager.Sensor.pressure`, :attr:`~lizzy.sensors.sensmanager.Sensor.fill_factor` and :attr:`~lizzy.sensors.sensmanager.Sensor.velocity` of each sensor.
        """
        if len(self.sensors) == 0:
            print("Cannot read sensors: no sensors have been created.")
            return
        sensor_readings = {}
        for sensor in self.sensors:
            sensor_readings[sensor.idx] = f"time: {sensor.time} s; resin pressure: {sensor.pressure} Pa; fill factor: {sensor.fill_factor}, resin velocity: {sensor.velocity} m/s"
        print(sensor_readings)
    
    def get_sensor_by_id(self, idx:int) -> Sensor:
        """Fetches a sensor by its index.
        """
        try:
            sensor = self.sensors_dict[idx]
        except:
            raise KeyError(f"Could not find sensor with id: {idx}")
        # TODO: not nice handling here
        return sensor
