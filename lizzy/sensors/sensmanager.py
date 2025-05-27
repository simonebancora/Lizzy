#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

class Sensor:
    def __init__(self, x, y, z):
        self.id = 0
        self.coords = np.array((x, y, z))
        self.pvals = None   # pressure
        self.vvals = None   # velocity
        self.fvals = None   # fill factor
        self.tvals = None   # time
        self.resin_arrived = False

        # temporary quick implementation node-based
        self.child_node = None
    
    def reset(self):
        self.pvals = []
        self.vvals = []
        self.fvals = []
        self.tvals = []
        self.resin_arrived = False
    

    def info(self) -> str:
        return f"Sensor ID: {self.id}; position: ({self.coords[0]}, {self.coords[1]}, {self.coords[2]}; child node ID: {self.child_node.id})"


class SensorManager:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} is a singleton and must not be instantiated.")
    sensors = []
    sensor_trigger_states = []

    @classmethod
    def add_sensor(cls, x, y, z):
        new_sensor = Sensor(x, y, z)
        new_sensor.id = len(cls.sensors)
        cls.sensors.append(new_sensor)
        
    
    @classmethod
    def initialise(cls, mesh):
        if len(cls.sensors) > 0:
            all_node_coords = mesh.nodes.XYZ
            for sensor in cls.sensors:
                distances = []
                for node_coords in all_node_coords:
                    distances.append(np.linalg.norm(sensor.coords - node_coords))
                id_closest_node = np.argmin(np.array(distances))
                sensor.child_node = mesh.nodes[id_closest_node]
            cls.sensor_trigger_states = np.array([False for s in cls.sensors])
    
    @classmethod
    def probe_current_solution(cls, p_array, v_array, f_array, current_time):
        if len(cls.sensors) > 0:
            for sensor in cls.sensors:
                sensor.tvals.append(current_time)
                sensor.pvals.append(p_array[sensor.child_node.id])
                sensor.fvals.append(f_array[sensor.child_node.id])
                sensor.vvals.append(v_array[sensor.child_node.id])

    @classmethod
    def reset_sensors(cls):
        if len(cls.sensors) > 0:
            for sensor in cls.sensors:
                sensor.reset()

    @classmethod
    def check_for_new_sensor_triggered(cls, fill_factor_array):
        triggered = False
        for sensor in cls.sensors:
            if fill_factor_array[sensor.child_node.id] >= 0.5:
                sensor.resin_arrived = True
        current_trigger_states = np.array([sensor.resin_arrived for sensor in cls.sensors])
        diff = current_trigger_states != cls.sensor_trigger_states
        if np.any(diff):
            cls.sensor_trigger_states = current_trigger_states
            triggered = True
        return triggered