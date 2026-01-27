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
from .construction import CreateNodes, CreateLines, CreateTriangles, CreateControlVolumes
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
        self.triangles : list[Triangle] = elements([])
        self.tetras = elements([])
        self.lines : list[Line] = lines([])
        self.CVs :list[CV] = []
        self.boundaries = mesh_reader.mesh_data['physical_nodes']
        self.preprocessed = False

        # Init methods:
        self.PopulateFromMeshData(self.mesh_data)
        self.CrossReferenceEntities()

        ################## ALL THIS BLOCK TO BE REMOVED
        # create mesh of CVs for visualisation only
        cv_mesh_nodes = []
        cv_mesh_conn = []
        nodes_counter = 0
        for cv in self.CVs:
            for two_lines_tri in cv.cv_lines:
                for line in two_lines_tri:
                    line_conn = []
                    p1 = line.p1
                    p2 = line.p2
                    cv_mesh_nodes.append(p1)
                    line_conn.append(nodes_counter)
                    nodes_counter += 1
                    cv_mesh_nodes.append(p2)
                    line_conn.append(nodes_counter)
                    nodes_counter += 1
                    cv_mesh_conn.append(line_conn)

        self.cv_mesh_nodes = cv_mesh_nodes
        self.cv_mesh_conn = cv_mesh_conn

    ################## ALL THIS BLOCK TO BE REMOVED

    def PopulateFromMeshData(self, mesh_data):
        """
        Takes mesh data dictionary and initialises all mesh attributes: nodes, lines, triangles.

        Parameters
        ----------
        mesh_data : dict
            Dictionary of all mesh data read from mesh file
        """
        self.nodes = CreateNodes(mesh_data)
        self.triangles = CreateTriangles(mesh_data, self.nodes)
        self.lines = CreateLines(mesh_data, self.triangles)

    def preprocess(self, material_manager: MaterialManager, fill_solver: FillSolver):
        """ Pre-processes the mesh before simulation. Assigns material properties to elements, creates control volumes (CVs), and prepares data structures for simulation."""
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
        self.CVs = CreateControlVolumes(self.nodes, fill_solver)
        # create a hashmap for CV id: [ids of supporting elements]
        print("Mesh pre-processing completed\n")



        #TODO: for numba:
        self.triangle_id_lists = [np.array(n.triangle_ids, dtype=np.int32) for n in self.nodes]




        self.preprocessed = True

    def CrossReferenceEntities(self):
        """
        Creates hierarchical connections between all objects that constitute the mesh: Nodes, Lines, Elements.
        The purpose is to make any given object accessible from any other given object, to which it would be linked as an attribute.
        Once this method is called on a mesh, all references should be created.

        Example
        --------
        Given a mesh which has been cross referenced, fetch the nodes of the fourth element:

        >>> nodes = mesh.elements[3].nodes
        """

        # go through nodes and cross reference connected nodes, to help fetch support CVs
        for node in self.nodes:
            connected_nodes_ids = []
            for tri in node.triangles:
                connected_nodes_ids.append(tri.node_ids)
            connected_nodes_ids = np.unique(connected_nodes_ids).tolist()
            connected_nodes_ids.remove(node.idx)
            node.node_ids = connected_nodes_ids

    def empty_cvs(self):
        for cv in self.CVs:
            cv.fill = 0
