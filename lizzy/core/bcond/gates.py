#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
import numpy as np


class Inlet():
    """A class representing an inlet boundary condition.

    Parameters
    ----------
    p_value : float
        Initial pressure value at the inlet [Pa].
    name : str, optional
        Label assigned to the inlet. Will be used to select the inlet in future operations. If none assigned, a default 'unnamed_inlet' name is given.
    """
    def __init__(self, p_value:float, name:str = "unnamed_inlet"):
        super().__init__()
        self.p_value = p_value
        self._p0 = p_value
        self.name = name
        self._assigned = False
        self._open = True
    
    @property
    def p_value(self) -> float:
        """Current pressure value [Pa]. Can be changed at any time.
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
    
    @property
    def is_open(self) -> bool:
        """Indicates whether the inlet is currently open (True) or closed (False). (read-only)
        """
        return self._open

    def reset(self):
        """Restores the inlet :attr:`~lizzy.bcond.bcond.Inlet.p_value` to the value assigned at creation time and sets it to open.
        """
        self.p_value = self._p0
        self._open = True
    
    def set_open(self, open: bool):
        """Set the inlet state to open or closed.

        Parameters
        ----------
        open : bool
            The state the inlet will be instantly set to: open (True) or closed (False).
        """
        self._open = open
    


@dataclass()
class SolverBCs:
    dirichlet_idx = np.array([], dtype=int)
    dirichlet_vals  = np.array([], dtype=float)
    p0_idx = np.array([], dtype=int)
