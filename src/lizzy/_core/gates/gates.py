#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from abc import ABC
from enum import Enum, auto

class InletType(Enum):
    PRESSURE = auto()
    FLOW_RATE = auto()


class Inlet(ABC):
    """Abstract class representing an inlet. :class:`~lizzy.gates.PressureInlet` and :class:`~lizzy.gates.FlowRateInlet` derive from this class.
    """
    def __init__(self, name:str, inlet_type:InletType):
        super().__init__()
        self._name = name
        self._type = inlet_type
        self._assigned = False
        self._open = True
    
    @property
    def name(self) -> str:
        """Unique name of the inlet. (read-only)
        """
        return self._name
    
    @property
    def is_open(self) -> bool:
        """Indicates whether the inlet is currently open (True) or closed (False). (read-only)
        """
        return self._open
    
    @property
    def type(self) -> InletType:
        return self._type

    def reset(self):
        """Restores the inlet :attr:`~lizzy.core.bcond.Inlet.p_value` to the value assigned at creation time and sets it to open.
        """
        self._open = True
    
    def set_open(self, open_state: bool):
        """Set the inlet state to open or closed.

        Parameters
        ----------
        open_state : bool
            The state the inlet will be set to: open (True) or closed (False).
        """
        self._open = open_state

class PressureInlet(Inlet):
    def __init__(self, name:str, p_value:float):
        super().__init__(name, InletType.PRESSURE)
        self._p_value = p_value
        self._p0 = p_value
    
    @property
    def p_value(self) -> float:
        """Current pressure value [Pa].
        """
        return self._p_value

    @p_value.setter
    def p_value(self, value: float):
        if value < 0:
            raise ValueError("p_value must be non-negative")
        self._p_value = value
    
    @property
    def p0(self) -> float:
        """Initial pressure value assigned at inlet creation time. (read-only)
        """
        return self._p0
    
    def reset(self):
        super().reset()
        self._p_value = self._p0



class FlowRateInlet(Inlet):
    def __init__(self, name:str, q_value:float):
        super().__init__(name, InletType.FLOW_RATE)
        self._q_value = q_value
        self._q0 = q_value
    
    @property
    def q_value(self) -> float:
        """Current pressure value [Pa].
        """
        return self._q_value

    @q_value.setter
    def q_value(self, value: float):
        if value < 0:
            raise ValueError("q_value must be non-negative")
        self._q_value = value
    
    @property
    def q0(self) -> float:
        """Initial pressure value assigned at inlet creation time. (read-only)
        """
        return self._q0
    
    def reset(self):
        super().reset()
        self._q_value = self._q0


class Vent:
    def __init__(self, name:str, vacuum_pressure:float=0.0):
        """A class respresenting a vent boundary. Vent vacuum pressure will be applied to all non-filled regions in the domain.

        Parameters
        ----------
        name : str
            Unique name of the vent.
        """
        self.name = name
        self._assigned = False
        self._vacuum_pressure = vacuum_pressure # Vacuum pressure value at the vent [Pa]

    @property
    def vacuum_pressure(self) -> float:
        """Vacuum pressure value [Pa].
        """
        return self._vacuum_pressure
    
    @vacuum_pressure.setter
    def vacuum_pressure(self, value: float):
        if value < 0:
            raise ValueError("vacuum_pressure must be non-negative")
        self._vacuum_pressure = value


