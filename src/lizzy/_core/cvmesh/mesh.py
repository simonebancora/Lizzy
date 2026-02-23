#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
import sys
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.io import Reader
    from lizzy._core.cvmesh.entities import Node, Line, BoundaryLine, Triangle, CV
    from .construction import MeshView
    from lizzy._core.materials import PorousMaterial, Rosette

import numpy as np
from .construction import MeshBuilder
from .collections import nodes, lines, elements


class Mesh:
    r"""
    A class representing a FE/CV mesh.

    The Mesh class provides methods for creating and manipulating a mesh. Takes a mesh_data dictionary coming from the mesh reader, and creates objects for all entities (nodes, elements, lines). Also creates the control volumes (CVs).

    Parameters
    ----------
    mesh_reader : IO.Reader
        Dictionary containing mesh data, returned by IO.Reader

    """
    def __init__(self):
        self.mesh_view : MeshView = None
        self.mesh_data = None
        self.nodes : list[Node] = nodes([])
        self.lines : list[Line] = lines([])
        self.boundary_lines : list[BoundaryLine] = lines([])
        self.triangles : list[Triangle] = elements([])
        self.tetras = elements([])
        self.CVs : list[CV] = []
        self.node_coords = np.array([])

    # Init method:
    def build_mesh(self, mesh_data):
        self.mesh_data = mesh_data
        mb = MeshBuilder()
        self.nodes, self.lines, self.boundary_lines, self.triangles, self.CVs, self.mesh_view = mb.build_mesh(mesh_data)
    
    def update_elements_with_assigned_material(self, element_idxs, material: PorousMaterial, rosette: Rosette):
        for idx in element_idxs:
            tri = self.triangles[idx]
            if material.is_isotropic:
                tri.k = material.k_princ
            else:
                u, v, w = rosette.project_along_normal(tri.n)
                R = np.array([u, v, w]).T
                tri.k = R @ material.k_princ @ R.T
            tri.porosity = material.porosity
            tri.h = material.thickness
            tri.material_assigned = True
    
    def assert_all_elements_have_material(self):
        for tri in self.triangles:
            if not tri.material_assigned:
                print(f"ERROR: Element with id {tri.idx} does not have an assigned material. Check material assignments.")
                sys.exit(1)

    def empty_cvs(self):
        for cv in self.CVs:
            cv.fill = 0
