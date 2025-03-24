#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from lizzy.cvmesh.constr import CreateNodes, CreateLines, CreateTriangles, CreateControlVolumes
from lizzy.cvmesh.collections import nodes, lines, elements
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lizzy.IO import IO

class Mesh:
    """
    A class representing a FE/CV mesh.

    The Mesh class provides methods for creating and manipulating a mesh. Takes a mesh_data dictionary coming from the mesh reader, and creates objects for all entities (nodes, elements, lines). Also creates the control volumes (CVs).

    Parameters
    ----------
    mesh_reader : IO.Reader
        Dictionary containing mesh data, returned by IO.Reader

    Attributes
    ----------
    nodes
        List of all nodes in the mesh.
    triangles
        List of all elements in the mesh.
    lines
        List of all lines (element edges) in the mesh. Lines shared by adjacent elements are repeated. Only boundary lines are unique.
    CVs
        List of all CVs in the mesh.
    """
    def __init__(self, mesh_reader):
        self.mesh_data = mesh_reader.mesh_data
        self.nodes = nodes([])
        self.triangles = elements([])
        self.lines = lines([])
        self.boundaries = mesh_reader.mesh_data['physical_nodes']

        # Init methods:
        self.PopulateFromMeshData(self.mesh_data)
        self.CrossReferenceEntities()
        self.CVs = CreateControlVolumes(self.nodes)
        print("Mesh pre-processing completed\n")

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
            connected_nodes_ids.remove(node.id)
            node.node_ids = connected_nodes_ids

    def EmptyCVs(self):
        for cv in self.CVs:
            cv.fill = 0
