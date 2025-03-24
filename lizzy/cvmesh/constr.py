#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from .collections import nodes, lines, elements
from . import entities as ent
from lizzy.materials import MaterialManager

def CreateNodes(mesh_data):
    """
    Creates a Nodes. Returns a "nodes" list.
    """
    nodes_coords = np.array(mesh_data['all_nodes_coords'])
    all_nodes = nodes([])
    for n, X in enumerate(nodes_coords):
        node = ent.Node(X)
        node.id = n
        all_nodes.append(node)
    all_nodes.XYZ = nodes_coords # redundant but might be useful
    all_nodes.N = len(nodes_coords)
    return all_nodes

def CreateLines(mesh_data, triangles):
    """
    Creates Lines. Returns a "lines" list.
    """
    all_lines = lines([])
    line_counter = 0
    for n, triangle in enumerate(triangles):
        #line 1
        line_1 = ent.Line(triangle.nodes[0], triangle.nodes[1])
        line_1.id = line_counter
        line_1.triangles.append(triangle)
        line_1.triangle_ids.append(triangle.id)
        line_counter += 1
        all_lines.append(line_1)
        # line 2
        line_2 = ent.Line(triangle.nodes[1], triangle.nodes[2])
        line_2.id = line_counter
        line_2.triangles.append(triangle)
        line_2.triangle_ids.append(triangle.id)
        line_counter += 1
        all_lines.append(line_2)
        # line 3
        line_3 = ent.Line(triangle.nodes[2], triangle.nodes[0])
        line_3.id = line_counter
        line_3.triangles.append(triangle)
        line_3.triangle_ids.append(triangle.id)
        line_counter += 1
        all_lines.append(line_3)

        # reference created lines to triangle
        triangle.lines.append(line_1)
        triangle.line_ids.append(line_1.id)
        triangle.lines.append(line_2)
        triangle.line_ids.append(line_2.id)
        triangle.lines.append(line_3)
        triangle.line_ids.append(line_3.id)

    all_lines.N = len(all_lines)
    return all_lines

def CreateTriangles(mesh_data, nodes):
    """
    Creates triangles. Returns a "triangles" list.

    Preliminary calculations (pre-processing) for tri elements.
    Put triangles in planes and calculate Jacobians and areas:
    A_el = A_xi * det(J) = 0.5 * abs(det(J))
    """
    conn = mesh_data['nodes_conn']
    all_triangles = elements([])
    for n, local_conn in enumerate(conn):
        node_1 = nodes[local_conn[0]]
        node_2 = nodes[local_conn[1]]
        node_3 = nodes[local_conn[2]]
        tri = ent.Triangle(node_1, node_2, node_3)
        tri.id = n
        tri.node_ids = [node_1.id, node_2.id, node_3.id]
        all_triangles.append(tri)
        # also assign triangle to nodes
        node_1.triangles.append(tri)
        node_1.triangle_ids.append(tri.id)
        node_2.triangles.append(tri)
        node_2.triangle_ids.append(tri.id)
        node_3.triangles.append(tri)
        node_3.triangle_ids.append(tri.id)

    # assign material_tag tag
    for key in mesh_data['physical_domains']:
        for i in mesh_data['physical_domains'][key]:
            all_triangles[i].material_tag = key

    # assign permeability to elements
    materials = MaterialManager.materials
    rosettes = MaterialManager.rosettes
    for tri in all_triangles:
        try:
            material = materials[tri.material_tag]
            rosette = rosettes[tri.material_tag]
            u, v, w = rosette.project_along_normal(tri.n)
            R = np.array([u, v, w]).T
            tri.k = R @ material.k_diag @ R.T
            tri.porosity = materials[tri.material_tag].porosity
            tri.h = materials[tri.material_tag].thickness
        except KeyError:
            exit(f"Mesh contains unassigned material tag: {tri.material_tag}")

    all_triangles.nodes_conn_table = mesh_data['nodes_conn'] # needed?
    all_triangles.N = len(all_triangles)
    return all_triangles

def CreateControlVolumes(nodes):
    # for every nodes:
    CVs = []
    for node in nodes:
        # retrieve elements that contain that node
        new_CV = ent.CV()
        new_CV.id = node.id
        new_CV.node = node
        new_CV.support_triangles = node.triangles
        new_CV.calculate_area_and_volume()
        CVs.append(new_CV)
    CVs = np.array(CVs)
    # reference support CVs
    for cv in CVs:
        connected_nodes = cv.node.node_ids
        cv.support_CVs = CVs[connected_nodes]
        cv.GetCVLines()
        cv.CheckFluxNormalOrientations()
    return CVs