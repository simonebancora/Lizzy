#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from functools import singledispatchmethod

class Rosette:
    """Rosette object to define the orientation of the material in the mesh elements. The rosette is always projected on each element along the element normal direction. Can be initialised by passing one vector, or 2 points.
    """
    def __init__(self, u=(1.0,1.0,1.0), p0=(0.0,0.0,0.0)):
        u = np.array(u)
        self.p0 = np.array(p0)
        self.u = p0 - u

    def project_along_normal(self, normal):
        u_normal = np.dot(self.u, normal) * normal
        u_project = self.u - u_normal
        u_project = u_project / np.linalg.norm(u_project)
        v_project = np.cross(u_project, normal)
        v_project = v_project / np.linalg.norm(v_project)
        return u_project, v_project, normal



class PorousMaterial:
    def __init__(self, k1:float, k2:float, k3:float,  porosity:float, thickness:float, name:str = "unnamed_material"):
        """
        Permeability tensor defined as principal permeability values k1, k2, k3 and by porosity and thickness.

        Parameters
        ----------
        k1: float
            Principal permeability in local direction e1.
        k2: float
            Principal permeability in local direction e2.
        theta: float
            Rotation angle in degrees, counter-clockwise.
        """
        self.k_diag = np.array([[k1, 0, 0],[0, k2, 0],[0, 0, k3]])
        self.porosity = porosity
        self.thickness = thickness
        self.name = name
        self._assigned = False

class MaterialManager:
    def __init__(self):
        self.assigned_materials : dict = {}
        self.assigned_rosettes : dict = {}
        self.existing_materials : dict = {}
    
    @singledispatchmethod
    def fetch_material(self, material_selector):
        return material_selector
    
    @fetch_material.register
    def _(self, material_selector:str):
        try:
            selected_material = self.existing_materials[material_selector]
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
            material_count = len(self.existing_materials)
            name = f"Material_{material_count}"
        new_material = PorousMaterial(k1, k2, k3, porosity, thickness, name)
        self.existing_materials[name] = new_material
        return new_material

    def assign_material(self, material_selector:str, mesh_tag:str, rosette:Rosette = None):
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
        selected_material = self.fetch_material(material_selector)
        if rosette is None:
            rosette = Rosette((1, 0, 0))
        selected_material._assigned = True
        self.assigned_materials[mesh_tag] = selected_material
        self.assigned_rosettes[mesh_tag] = rosette