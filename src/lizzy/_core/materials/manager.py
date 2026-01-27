#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import numpy as np
from .materials import PorousMaterial
from .rosette import Rosette

class MaterialManager:
    """Manager for all material operations.
    """
    def __init__(self):
        self._existing_materials : dict[str, PorousMaterial] = {}
        self._assigned_materials : dict[str, PorousMaterial] = {}
        self._assigned_rosettes : dict[str, Rosette] = {}
    
    @property
    def assigned_materials(self) -> dict[str, PorousMaterial]:
        """Dictionary of materials that have been assigned to mesh regions (read-only).
        """
        return self._assigned_materials
    
    @property
    def assigned_rosettes(self) -> dict[str, Rosette]:
        """Dictionary of rosettes assigned to materials in mesh regions (read-only).
        """
        return self._assigned_rosettes
    
    @property
    def existing_materials(self) -> dict[str, PorousMaterial]:
        """Dictionary of materials that exist in the model, but may have not been assigned yet (read-only).
        """
        return self._existing_materials
    
    def fetch_material(self, material_selector:str):
        try:
            selected_material = self._existing_materials[material_selector]
        except KeyError:
            raise KeyError(f"Inlet '{material_selector}' is not found in existing inlets. Check the name, or create the inlet first using `LizzyModel.create_inlet`.")
        return selected_material

    def create_material(self, name:str, k_vals : tuple[float, float, float], porosity: float, thickness: float):
        if name in self._existing_materials.keys():
            print(f"ERROR: the material name '{name}' is not unique. Another material with the same name already exists in the model.")
            sys.exit(1)
        new_material = PorousMaterial(name, k_vals, porosity, thickness)
        self._existing_materials[name] = new_material
        return new_material

    def create_rosette(self, name:str, u: tuple[float, float, float] = (1.0, 0, 0)):
        if name in self._assigned_rosettes.keys():
            print(f"ERROR: the rosette name '{name}' is not unique. Another rosette with the same name already exists in the model.")
            sys.exit(1)
        new_rosette = Rosette(name, u)
        self._assigned_rosettes[name] = new_rosette
        return new_rosette

    def _fetch_rosette(self, rosette_selector: str):
        try:
            selected_rosette = self._assigned_rosettes[rosette_selector]
        except KeyError:
            raise KeyError(f"Rosette '{rosette_selector}' is not found in assigned rosettes. Check the name, or create the rosette first using `LizzyModel.create_rosette`.")
        return selected_rosette

    def assign_material(self, material_selector:str, mesh_tag:str, rosette_selector:str | Rosette = None):
        selected_material : PorousMaterial = self.fetch_material(material_selector)
        if rosette_selector is None:
            rosette = Rosette((1, 0, 0))
        elif isinstance(rosette_selector, str):
            rosette = self._fetch_rosette(rosette_selector)
        else:
            rosette = rosette_selector
        selected_material.assigned = True
        self._assigned_materials[mesh_tag] = selected_material
        self._assigned_rosettes[mesh_tag] = rosette