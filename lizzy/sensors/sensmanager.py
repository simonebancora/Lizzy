#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from lizzy.cvmesh.entities import Node
from lizzy.cvmesh.cvmesh import Mesh

class Sensor:
    """This class represents a virtual sensor in the model.

    Parameters
    ----------
    x : float
        x coordinate of the sensor.
    y : float
        y coordinate of the sensor.
    z : float
        z coordinate of the sensor.
    """
    def __init__(self, x:float, y:float, z:float):
        self._idx = 0
        self._coords = np.array((x, y, z))
        self._pvals = None   # pressure
        self._vvals = None   # velocity
        self._fvals = None   # fill factor
        self._tvals = None   # time
        self.resin_arrived = False

        # temporary quick implementation node-based
        self.child_node:Node = None
    
    def _reset(self):
        """Resets all solution values in the sensor (pressure, velocity, fill factor and time). Maintains the sensor in place and active at the same location. This method is called automatically when a new simulation is initialised.
        """
        self._pvals = []
        self._vvals = []
        self._fvals = []
        self._tvals = []
        self.resin_arrived = False

    @property
    def idx(self) -> int:
        """The unique index of the sensor.
        """
        return self._idx
    
    @property
    def position(self) -> np.ndarray:
        """The (x,y,z) position of the sensor in 3D space. (read-only)
        """
        return self._coords
    
    @property
    def pressure(self) -> float:
        """The current value of resin pressure (Pa) at the sensor location. (read-only)
        """
        return self._pvals[-1]

    @property
    def velocity(self) -> np.ndarray:
        """The current value of resin velocity (m/s) at the sensor location. (read-only)
        """
        return self._vvals[-1]
    
    @property
    def fill_factor(self) -> float:
        """The current value of resin fill factor at the sensor location. (read-only)
        """
        return self._fvals[-1]
    
    @property
    def time(self) -> float:
        """The current time in the simulation. (read-only)
        """
        return self._tvals[-1]
    
    def get_latest(self, key:str):
        match key:
            case "pressure":
                return self.pressure
            case "velocity":
                return self.velocity
            case "fill_factor":
                return self.fill_factor
            case "time":
                return self.time
            case _:
                raise KeyError(f"Unrecognised sensor reading request: {key}")

    def info(self) -> str:
        """Returns basic information about the sensor: its ID, position and the ID of the mesh node it is attached to.
        """
        return f"Sensor ID: {self.idx}; position: ({self.position[0]}, {self.position[1]}, {self.position[2]}; child node ID: {self.child_node.idx})"


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
