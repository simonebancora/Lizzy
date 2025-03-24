#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
import numpy as np

class Boundary:
    def __init__(self, physical_tag:str):
        self.physical_tag = physical_tag

class Inlet(Boundary):
    def __init__(self, physical_tag:str, p_value:float):
        super().__init__(physical_tag)
        self.p_value = p_value

class BCManager:
    def __init__(self):
        self.inlets = []

    def add_inlet(self, *inlets:Inlet):
        for inlet in inlets:
            if inlet not in self.inlets:
                self.inlets.append(inlet)

    def remove_inlet(self, *inlets: Inlet):
        for inlet in inlets:
            try:
                self.inlets.remove(inlet)
            except ValueError:
                print (f"Inlet '{inlet.physical_tag}' not assigned in BCManager.")


@dataclass()
class SolverBCs:
    dirichlet_idx = np.array([], dtype=int)
    dirichlet_vals  = np.array([], dtype=float)
    p0_idx = np.array([], dtype=int)
