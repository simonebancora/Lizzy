#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
from functools import singledispatchmethod
import numpy as np

class Boundary:
    def __init__(self):
        pass

class Inlet(Boundary):
    def __init__(self, p_value:float, name:str = "unnamed_inlet"):
        super().__init__()
        self.p0 = p_value
        self.p_value = p_value
        self.name = name
        self.assigned = False
        self.open = True

    def reset(self):
        self.p_value = self.p0

def create_inlet(initial_pressure_value:float, name:str = "unnamed_inlet"):
    # TODO: handle arguments bad input
    # TODO: not clear how names are used. Set a system to select inlets both by name and by tag
    return Inlet(initial_pressure_value, name)

class BCManager:
    def __init__(self):
        self.assigned_inlets : dict[str, Inlet] = {}
        self.existing_inlets : dict[str, Inlet] = {}

    def create_inlet(self, initial_pressure_value:float, name:str = None):
        if name is None:
            inlet_count = len(self.existing_inlets)
            name = f"Inlet_{inlet_count}"
        new_inlet = create_inlet(initial_pressure_value, name)
        self.existing_inlets[name] = new_inlet
        return new_inlet

    @singledispatchmethod
    def fetch_inlet(self, inlet_selector:Inlet):
        return inlet_selector

    @fetch_inlet.register
    def _(self, inlet_selector:str):
        try:
            selected_inlet = self.existing_inlets[inlet_selector]
        except KeyError:
            raise KeyError(f"Inlet '{inlet_selector}' is not found in existing inlets. Check the name, or create the inlet first using `LizzyModel.create_inlet`.")
        return selected_inlet

    def assign_inlet(self, inlet_selector, boundary_tag:str):
        selected_inlet = self.fetch_inlet(inlet_selector)
        if selected_inlet not in self.assigned_inlets.values():
            self.assigned_inlets[boundary_tag] = selected_inlet
            selected_inlet.assigned = True

    
    # TODO: functionality will be added to change the pressure over time, along different time interpolation options
    def change_inlet_pressure(self, inlet_selector, pressure_value:float, mode:str = "set"):
        selected_inlet = self.fetch_inlet(inlet_selector)
        match mode:
            case "set":
                selected_inlet.p_value = pressure_value
            case "delta":
                selected_inlet.p_value += pressure_value
            case _:
                raise KeyError

    def open_inlet(self,inlet_selector):
        selected_inlet = self.fetch_inlet(inlet_selector)
        selected_inlet.open = True

    def close_inlet(self,inlet_selector):
        selected_inlet = self.fetch_inlet(inlet_selector)
        selected_inlet.open = False
    
    def reset_inlets(self):
        for tag, inlet in self.assigned_inlets.items():
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
