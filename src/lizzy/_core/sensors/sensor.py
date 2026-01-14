#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy.entities import Node

import numpy as np

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
