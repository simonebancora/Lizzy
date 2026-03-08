#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from .gates import Inlet, PressureInlet, FlowRateInlet, Vent
from typing import Literal
from lizzy.exceptions import ConfigurationError

class GatesManager:
    """Manager for all boundary condition operations.
    """
    def __init__(self):
        self._created_inlets : dict[str, Inlet] = {}
        self._assigned_inlets : dict[str, Inlet] = {}
        self._created_vents : dict[str, Vent] = {}
        self._assigned_vents : dict[str, Vent] = {}
    
    @property
    def assigned_inlets(self) -> dict[str, Inlet]:
        """Dictionary of inlets that exist and have been assigned to boundaries (read-only).
        """
        return self._assigned_inlets
    
    @property
    def assigned_vents(self) -> dict[str, Vent]:
        """Dictionary of vents that exist and have been assigned to boundaries (read-only).
        """
        return self._assigned_vents

    @property
    def existing_inlets(self) -> dict[str, Inlet]:
        """Dictionary of inlets that exist in the model (read-only).
        """
        return self._created_inlets

    def create_pressure_inlet(self, name:str, initial_pressure_value:float) -> Inlet:
        new_inlet = PressureInlet(name, initial_pressure_value)
        self._created_inlets[name] = new_inlet
        return new_inlet
    
    def create_flowrate_inlet(self, name:str, initial_flowrate_value:float) -> Inlet:
        new_inlet = FlowRateInlet(name, initial_flowrate_value)
        self._created_inlets[name] = new_inlet
        return new_inlet
    
    def create_vent(self, name:str, vacuum_pressure:float=0.0) -> Vent:
        new_vent = Vent(name, vacuum_pressure)
        self._created_vents[name] = new_vent
        return new_vent



    def _fetch_inlet(self, inlet_selector:Inlet | str) -> Inlet:
        if type(inlet_selector) is Inlet:
            return inlet_selector
        else:
            try:
                selected_inlet = self._created_inlets[inlet_selector]
            except KeyError:
                raise KeyError(f"Inlet '{inlet_selector}' is not found in existing inlets. Check the name, or create the inlet first.")
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
    
    def assign_vent(self, vent_selector:Vent | str, boundary_tag:str):
        """Selects a vent from existing ones and assigns it to the indicated mesh boundary.

        Parameters
        ----------
        vent_selector : Vent | str
            Either the vent object to assign, or the name of an existing vent.
        boundary_tag : str
            An existing mesh boundary tag where to assign the vent.
        """
        if type(vent_selector) is Vent:
            selected_vent = vent_selector
        else:
            try:
                selected_vent = self._created_vents[vent_selector]
            except KeyError:
                raise KeyError(f"Vent '{vent_selector}' is not found in existing vents. Check the name, or create the vent first.")
        if selected_vent not in self._assigned_vents.values():
            if len(self._assigned_vents) > 0:
                raise ConfigurationError("Multiple vents assigned to the model. Currently only one vent is supported.")
            self._assigned_vents[boundary_tag] = selected_vent
            selected_vent._assigned = True
    
    # TODO: functionality should be added to change the pressure over time, along different time interpolation options
    def change_inlet_pressure(self, inlet_selector:Inlet | str, pressure_value:float, mode: Literal["set", "delta"] = "set"):
        selected_inlet = self._fetch_inlet(inlet_selector)
        match mode:
            case "set":
                selected_inlet.p_value = pressure_value
            case "delta":
                selected_inlet.p_value += pressure_value
            case _:
                raise KeyError

    def open_inlet(self, inlet_selector:Inlet | str):
        selected_inlet = self._fetch_inlet(inlet_selector)
        selected_inlet.set_open(True)

    def close_inlet(self, inlet_selector:Inlet | str):
        selected_inlet = self._fetch_inlet(inlet_selector)
        selected_inlet.set_open(False)
    
    def reset_inlets(self):
        for tag, inlet in self._assigned_inlets.items():
            inlet.reset()

    def assert_unique_boundary_assignments(self):
        """Checks that each boundary has at most one inlet or vent assigned, and raises an error if this is not the case.
        """
        boundary_names = list(self._assigned_inlets.keys()) + list(self._assigned_vents.keys())
        if len(boundary_names) != len(set(boundary_names)):
            raise ConfigurationError("Multiple inlets or vents assigned to the same boundary. Check the assigned inlets and vents for duplicate boundary tags.")