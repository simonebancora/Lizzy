#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.solver import FillSolver
    from lizzy._core.io import Reader
    from lizzy._core.materials import MaterialManager, Rosette, PorousMaterial
    from lizzy._core.cvmesh.entities import Node, Line, Triangle, CV

import numpy as np
from .construction import create_control_volumes, MeshBuilder
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
    def __init__(self, mesh_reader:Reader):
        self.mesh_data = mesh_reader.mesh_data
        self.nodes : list[Node] = nodes([])
        self.lines : list[Line] = lines([])
        self.triangles : list[Triangle] = elements([])
        self.tetras = elements([])
        self.CVs :list[CV] = []
        self.boundaries = mesh_reader.mesh_data['physical_nodes']
        self.preprocessed = False

        # Init methods:
        self.mb = MeshBuilder()
        self.nodes, self.lines, self.triangles = self.mb.build_mesh(self.mesh_data)

    def preprocess(self, material_manager: MaterialManager, fill_solver: FillSolver):
        """ Pre-processes the mesh before simulation. Assigns material properties to elements, creates control volumes (CVs), and prepares data structures for simulation."""
        self.CVs = create_control_volumes(self.nodes, fill_solver)
        materials = material_manager.assigned_materials
        rosettes = material_manager.assigned_rosettes
        for tri in self.triangles:
            try:
                material : PorousMaterial = materials[tri.material_tag]
                if material.is_isotropic:
                    tri.k = material.k_princ
                else:
                    rosette : Rosette = rosettes[tri.material_tag]
                    u, v, w = rosette.project_along_normal(tri.n)
                    R = np.array([u, v, w]).T
                    tri.k = R @ material.k_princ @ R.T
                tri.porosity = materials[tri.material_tag].porosity
                tri.h = materials[tri.material_tag].thickness
            except KeyError:
                exit(f"Mesh contains unassigned material tag: {tri.material_tag}")
        # create a hashmap for CV id: [ids of supporting elements]
        print("Mesh pre-processing completed\n")



        #TODO: for numba:
        self.triangle_id_lists = [np.array(n.triangle_ids, dtype=np.int32) for n in self.nodes]




        self.preprocessed = True

    def empty_cvs(self):
        for cv in self.CVs:
            cv.fill = 0
