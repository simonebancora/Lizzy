#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

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
        """Fetch an existing material by its label.
        Parameters
        ----------
        material_selector : str
            Label of the material to fetch.
        Returns
        -------
        :class:`PorousMaterial`
            Instance of the selected material.
        """
        try:
            selected_material = self._existing_materials[material_selector]
        except KeyError:
            raise KeyError(f"Inlet '{material_selector}' is not found in existing inlets. Check the name, or create the inlet first using `LizzyModel.create_inlet`.")
        return selected_material
    

    def create_material(self, k1: float, k2: float, k3: float, porosity: float, thickness: float, name: str = None):
        """Create a new material that can then be selected and used in the model.

        Parameters
        ----------
        k1 : float
            Permeability in the first principal direction.
        k2 : float
            Permeability in the second principal direction.
        k3 : float
            Permeability in the third principal direction.
        porosity : float
            Volumetric porosity of the material (porosity = 1 - fibre volume fraction).
        thickness : float
            Thickness of the material [mm].
        name : str, optional
            Label assigned to the material. Necessary to select the material during assignment. If none assigned, a default 'Material_{N}'name is given, where N is an incremental number of existing materials.

        Returns
        -------
        :class:`PorousMaterial`
            Instance of the created material.
        """
        if name is None:
            material_count = len(self._existing_materials)
            name = f"Material_{material_count}"
        new_material = PorousMaterial(k1, k2, k3, porosity, thickness, name)
        self._existing_materials[name] = new_material
        return new_material

    def create_rosette(self, p1: tuple[float, float, float] = (1.0, 0, 0), p0: tuple[float, float, float] = (0.0, 0.0, 0.0), name: str = None):
        """Create a new rosette that can then be selected and used in the model.

        Parameters
        ----------
        p1 : tuple[float, float, float]
            The first point defining the first axis of the rosette (k1 direction).
        p0 : tuple[float, float, float]
            The second point defining the first axis of the rosette (k1 direction). Default is (0,0,0).
        name : str, optional
            Label assigned to the rosette. Necessary to select the rosette during assignment. If none assigned, a default 'Rosette_{N}'name is given, where N is an incremental number of existing rosettes.

        Returns
        -------
        :class:`Rosette`
            Instance of the created rosette.
        """
        if name is None:
            rosette_count = len(self._assigned_rosettes)
            name = f"Rosette_{rosette_count}"
        new_rosette = Rosette(p1, p0, name)
        self._assigned_rosettes[name] = new_rosette
        return new_rosette

    def _fetch_rosette(self, rosette_selector: str):
        """Fetch an existing rosette by its label.

        Parameters
        ----------
        rosette_selector : str
            Label of the rosette to fetch.

        Returns
        -------
        :class:`Rosette`
            Instance of the selected rosette.
        """
        try:
            selected_rosette = self._assigned_rosettes[rosette_selector]
        except KeyError:
            raise KeyError(f"Rosette '{rosette_selector}' is not found in assigned rosettes. Check the name, or create the rosette first using `LizzyModel.create_rosette`.")
        return selected_rosette

    def assign_material(self, material_selector:str, mesh_tag:str, rosette_selector:str | Rosette = None):
        """Assign an existing material to a labeled mesh region.

        Parameters
        ----------
        material_selector : str
            Label of the material to assign. Must correspond to an existing material created with `LizzyModel.create_material`.
        mesh_tag : str
            Label of the mesh region where to assign the material.
        rosette : Rosette, optional
            Orientation rosette to apply to the material. If none provided, a default rosette with k1 aligned with the global X axis is assigned.
        """
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