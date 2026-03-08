#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
from lizzy._core.cvmesh.entities import Node, Line, BoundaryLine, Triangle, CV

class MeshView:
    def __init__(self):
        self.n_nodes:int=0
        self.n_lines:int=0
        self.n_triangles:int=0
        self.node_idx_to_node_idxs: list[np.ndarray] = []
        self.node_idx_to_tri_idxs: list[np.ndarray] = []
        self.node_idx_to_flux_ndarray: list[np.ndarray] = []
        self.phys_boundary_names_set:set[str] = set()
        self.phys_boundary_name_to_node_idxs:dict = {} #for dirichlet mostly
        self.phys_boundary_name_to_boundary_line_idxs:dict = {}
        self.boundary_line_idx_to_node_idxs: np.ndarray = None
        self.boundary_line_idx_to_tri_idx:np.ndarray = None


class MeshBuilder:
    def __init__(self):
        self.n_nodes = 0
        self.n_triangles = 0
        self.n_lines = 0
        self.node_idx_to_node_idxs = None
        self.node_idx_to_line_idxs = None
        self.node_idx_to_tri_idxs_buffer = None
        self.node_idx_to_tri_idxs = None

        self.line_idx_to_node_idxs = None
        self.line_idx_to_line_idxs = None
        self.line_idx_to_triangle_idxs = None

        self.triangle_idx_to_node_idxs = None
        self.triangle_idx_to_triangle_idxs = None
        self.triangle_idx_to_line_idxs = None

        self.node_idx_to_tri_idxs_for_fill_solver = None

    
    def create_cross_referencing_maps(self, n_nodes, n_lines, n_triangles, tri_conn, physical_lines_conn):
        capacity_tris_per_node = 8 # initial buffer size
        node_idx_to_tri_idxs_buffer = np.full((n_nodes, capacity_tris_per_node), -1, dtype=np.int32)
        tri_idxs_local_pointer = np.zeros(n_nodes, dtype=np.uint8)
        triangle_idx_to_line_idxs = np.empty((n_triangles, 3), dtype=np.uint32)
        line_idx_to_node_idxs = np.empty((n_lines, 2), dtype=np.uint32)
        boundary_line_idx_to_tri_idx = np.full(len(physical_lines_conn), -1, dtype=np.int32)

        line_nodes_from_conn_selectors = [[0,1],[1,2],[2,0]]
        for tri_id in range(n_triangles):
            local_conn = tri_conn[tri_id]

            # populate `line_idx_to_node_idxs`
            local_conn_pairs = [(local_conn[pair[0]], local_conn[pair[1]]) for pair in line_nodes_from_conn_selectors]
            for j in range(3):
                line_idx = tri_id*3+j
                local_node_idxs = local_conn_pairs[j]
                line_idx_to_node_idxs[line_idx] = local_node_idxs
            
                # populate `triangle_idx_to_line_idxs`
                triangle_idx_to_line_idxs[tri_id, j] = line_idx

            # populate `node_idx_to_tri_idxs_buffer`
            for local_node_id_selector in range(3):
                node_id = local_conn[local_node_id_selector]
                # check if we still have room for more ids
                if tri_idxs_local_pointer[node_id] > capacity_tris_per_node - 1:
                    # increase bufefr size
                    capacity_tris_per_node *=2
                    node_idx_to_tri_idxs_buffer = np.resize(node_idx_to_tri_idxs_buffer, (n_nodes, capacity_tris_per_node))
                # write the triangle id in the buffer (which is initially 5 tris per node)
                node_idx_to_tri_idxs_buffer[node_id, tri_idxs_local_pointer[node_id]] = tri_id
                # move local pointer
                tri_idxs_local_pointer[node_id] +=1
            
            # populate "boundary_line_idx_to_tri_idx"
            tri_node_ids_set = set(local_conn)
            for i in range(len(physical_lines_conn)):
                line_ids_set = set(physical_lines_conn[i])
                if line_ids_set.issubset(tri_node_ids_set):
                    boundary_line_idx_to_tri_idx[i] = tri_id
                    break
        
         
        # store
        self.node_idx_to_tri_idxs_buffer = node_idx_to_tri_idxs_buffer
        self.line_idx_to_node_idxs = line_idx_to_node_idxs
        self.triangle_idx_to_node_idxs = tri_conn
        self.triangle_idx_to_line_idxs = triangle_idx_to_line_idxs

        # check that all boundary lines have been assigned a valid tri idx (none negative)
        assert np.all(boundary_line_idx_to_tri_idx >= 0) # TODO: add some logging here 
        return boundary_line_idx_to_tri_idx

    def create_entities(self, n_nodes, n_triangles, n_lines, node_coords, tri_conn, physical_lines_conn, boundary_line_idx_to_tri_idx):
        # preallocate lists
        new_nodes = [None]*n_nodes
        new_lines = [None]*n_lines
        new_boundary_lines = [None]*len(physical_lines_conn)
        new_triangles = [None]*n_triangles
        # create nodes
        for i in range(n_nodes):
            new_nodes[i] = Node(node_coords[i,0], node_coords[i,1], node_coords[i,2], i)
        # create lines
        for i in range(n_lines):
            local_conn = self.line_idx_to_node_idxs[i]
            local_node_objs = [new_nodes[idx] for idx in local_conn]
            new_lines[i] = Line(*local_node_objs, i)
        # create triangles
        for i in range(n_triangles):
            local_nodes_conn = self.triangle_idx_to_node_idxs[i]
            local_node_objs = [new_nodes[idx] for idx in local_nodes_conn]
            local_lines_conn = self.triangle_idx_to_line_idxs[i]
            local_line_objs = [new_lines[idx] for idx in local_lines_conn]
            new_triangles[i] = Triangle(*local_node_objs, *local_line_objs, i)
        # create boundary lines:
        for i in range(len(physical_lines_conn)):
            local_conn = physical_lines_conn[i]
            local_node_objs = [new_nodes[idx] for idx in local_conn]
            new_boundary_lines[i] = BoundaryLine(*local_node_objs, i, new_triangles[boundary_line_idx_to_tri_idx[i]])
        
        return new_nodes, new_lines, new_triangles, new_boundary_lines

    def assign_material_tags_to_elements(self, mesh_data, triangles:list[Triangle]):
        # assign material_tag tag. key is a string (name of physical group)
        for key in mesh_data['physical_domains']:
            for i in mesh_data['physical_domains'][key]:
                triangles[i].material_tag = key



    def assign_varying_number_references(self, nodes:list[Node], triangles):
        node_idx_to_node_idxs = [None]*len(nodes)
        node_idx_to_tri_idxs = [None]*len(nodes)
        
        for i in range(len(nodes)):
            # assign triangles to nodes (varying number)
            tri_ids_buffer = self.node_idx_to_tri_idxs_buffer[i]
            tri_ids = tri_ids_buffer[tri_ids_buffer >= 0]
            node_idx_to_tri_idxs[i] = np.array(tri_ids)
            nodes[i].triangle_ids = tri_ids
            triangle_objs = [triangles[idx] for idx in tri_ids]
            nodes[i].triangles = triangle_objs

            connected_node_idxs = [idx for triangle in triangle_objs for idx in triangle.node_ids]
            connected_node_idxs = list(set(connected_node_idxs)-{i})
            nodes[i].node_ids = connected_node_idxs
            nodes[i].nodes = [nodes[idx] for idx in connected_node_idxs]
            node_idx_to_node_idxs[i] = np.array(connected_node_idxs)
        self.node_idx_to_node_idxs = node_idx_to_node_idxs
        self.node_idx_to_tri_idxs = node_idx_to_tri_idxs
        return node_idx_to_node_idxs, node_idx_to_tri_idxs

            
    def build_mesh(self, mesh_data):
        print("Creating Mesh...")
        mesh_view = MeshView()
        tri_conn:np.ndarray = mesh_data['nodes_conn']
        node_coords:np.ndarray = mesh_data['all_nodes_coords']
        n_nodes = node_coords.shape[0]
        n_triangles = tri_conn.shape[0]
        n_lines = n_triangles*3
        mesh_view.n_nodes = n_nodes
        mesh_view.n_lines = n_lines
        mesh_view.n_triangles = n_triangles
        physical_lines_conn = mesh_data["physical_lines_conn"]
        boundary_line_idx_to_tri_idx = self.create_cross_referencing_maps(n_nodes, n_lines, n_triangles, tri_conn, physical_lines_conn)
        phys_boundary_name_to_boundary_line_idxs:dict = mesh_data["physical_lines"]
        mesh_view.phys_boundary_names_set = set(phys_boundary_name_to_boundary_line_idxs.keys())
        mesh_view.phys_boundary_name_to_node_idxs = mesh_data['physical_nodes']
        mesh_view.phys_boundary_name_to_boundary_line_idxs = phys_boundary_name_to_boundary_line_idxs
        mesh_view.boundary_line_idx_to_node_idxs = physical_lines_conn
        new_nodes, new_lines, new_triangles, new_boundary_lines = self.create_entities(n_nodes, n_triangles, n_lines, node_coords, tri_conn, physical_lines_conn, boundary_line_idx_to_tri_idx)
        node_idx_to_node_idxs, node_idx_to_tri_idxs = self.assign_varying_number_references(new_nodes, new_triangles)
        mesh_view.node_idx_to_node_idxs = node_idx_to_node_idxs
        mesh_view.node_idx_to_tri_idxs = node_idx_to_tri_idxs
        mesh_view.boundary_line_idx_to_tri_idx = boundary_line_idx_to_tri_idx
        cvs = self.create_control_volumes(new_nodes)

        self.assign_material_tags_to_elements(mesh_data, new_triangles)


        return new_nodes, new_lines, new_boundary_lines, new_triangles, cvs, mesh_view


    def create_control_volumes(self, nodes : list[Node]):
        # for every nodes:
        n_nodes = len(nodes)
        CVs : list[CV] = [None]*n_nodes
        for i in range(n_nodes):
            CVs[i] = CV(nodes[i])
        # reference support CVs
        for cv in CVs:
            connected_nodes = cv.node.node_ids
            cv.support_CVs = [CVs[i] for i in connected_nodes]
        return np.array(CVs)


    

