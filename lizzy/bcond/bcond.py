#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
from functools import singledispatchmethod
import numpy as np
from typing import Literal


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
    


class BCManager:
    """Manager for all boundary condition operations.
    """
    def __init__(self):
        self._assigned_inlets : dict[str, Inlet] = {}
        self._existing_inlets : dict[str, Inlet] = {}
    
    @property
    def assigned_inlets(self) -> dict[str, Inlet]:
        """Dictionary of inlets that exist and have been assigned to boundaries (read-only).
        """
        return self._assigned_inlets

    @property
    def existing_inlets(self) -> dict[str, Inlet]:
        """Dictionary of inlets that exist in the model (read-only).
        """
        return self._existing_inlets

    def create_inlet(self, initial_pressure_value:float, name:str = None) -> Inlet:
        """Creates a new inlet and add it to the :attr:`~lizzy.bcond.bcond.BCManager.existing_inlets` dictionary.

        Parameters
        ----------
        initial_pressure_value : float
            Initial pressure value at the inlet.
        name : str, optional
            Label assigned to the inlet. Will be used to select the inlet in future operations. If none assigned, a default 'Inlet_{N}'name is given, where N is an incremental number of existing inlets.

        Returns
        -------
        :class:`~lizzy.bcond.bcond.Inlet`
            The created inlet object.
        """
        if name is None:
            inlet_count = len(self._existing_inlets)
            name = f"Inlet_{inlet_count}"
        new_inlet = Inlet(initial_pressure_value, name)
        self._existing_inlets[name] = new_inlet
        return new_inlet

    def _fetch_inlet(self, inlet_selector:Inlet | str) -> Inlet:
        if type(inlet_selector) is Inlet:
            return inlet_selector
        else:
            try:
                selected_inlet = self._existing_inlets[inlet_selector]
            except KeyError:
                raise KeyError(f"Inlet '{inlet_selector}' is not found in existing inlets. Check the name, or create the inlet first using `LizzyModel.create_inlet`.")
            return selected_inlet

    def assign_inlet(self, inlet_selector:Inlet | str, boundary_tag:str):
        #TODO: I dont like that the boundary tag is not checked against existing here. The check only happens at runtime by solver.
        """Selects an inlet from existing ones and assigns it to the indicated mesh boundary.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        boundary_tag : str
            An existing mesh boundary tag where to assign the inlet.
        """
        selected_inlet = self._fetch_inlet(inlet_selector)
        if selected_inlet not in self._assigned_inlets.values():
            self._assigned_inlets[boundary_tag] = selected_inlet
            selected_inlet._assigned = True

    
    # TODO: functionality should be added to change the pressure over time, along different time interpolation options
    def change_inlet_pressure(self, inlet_selector:Inlet | str, pressure_value:float, mode: Literal["set", "delta"] = "set"):
        """Changes the pressure value at the selected inlet to a new value, according to the selected mode.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        pressure_value : float
            The new pressure value to set at the inlet.
        mode : {'set', 'delta'}, optional
            How to apply the new pressure value:

            - ``set`` (default): directly set the new pressure value.
            - ``delta``: increment the existing pressure by the given value.
        Raises
        ------
        KeyError
            If the `mode` is not one of the allowed values.
        """
        selected_inlet = self._fetch_inlet(inlet_selector)
        match mode:
            case "set":
                selected_inlet.p_value = pressure_value
            case "delta":
                selected_inlet.p_value += pressure_value
            case _:
                raise KeyError

    def open_inlet(self, inlet_selector:Inlet | str):
        """Sets the selected inlet state to `open`. When open, the inlet applies its p_value as a Dirichlet boundary condition.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        """
        selected_inlet = self._fetch_inlet(inlet_selector)
        selected_inlet.set_open(True)

    def close_inlet(self, inlet_selector:Inlet | str):
        """Sets the selected inlet state to `closed`. When closed, the inlet acts as a Neumann natural boundary condition (no flux).

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        
        Note
        ----
        An inlet can be opened and closed at any time during the simulation to simulate valve operations. The stored p_value is preserved when the inlet is closed.
        """
        selected_inlet = self._fetch_inlet(inlet_selector)
        selected_inlet.set_open(False)
    
    def reset_inlets(self):
        """Calls the :meth:`~lizzy.bcond.bcond.Inlet.reset` method on all inlets currently present in the :attr:`~lizzy.bcond.bcond.BCManager.assigned_inlets` dictionary."""
        for tag, inlet in self._assigned_inlets.items():
            inlet.reset()

 
    # def remove_inlet(self, *inlets: Inlet):
    #     for inlet in inlets:
    #         try:
    #             self.inlets.remove(inlet)
    #         except ValueError:
    #             print (f"Inlet '{inlet.physical_tag}' not assigned in BCManager.")


@dataclass()
class SolverBCs:
    dirichlet_idx = np.array([], dtype=int)
    dirichlet_vals  = np.array([], dtype=float)
    p0_idx = np.array([], dtype=int)
