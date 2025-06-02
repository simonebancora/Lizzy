#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
# from numba import njit


class VelocitySolver:
    def __init__(self, triangles):
        self.B = any
        self.nodes_conn = any
        self.precalculate_B(triangles)

    def precalculate_B(self, triangles):
        """precalculate vectorised coefficient B of shape function gradients for velocity: v = B * p"""
        b_ncol = triangles[0].grad_N.shape[1]
        self.B = np.empty((len(triangles), 3, b_ncol), dtype=object)
        for i in range(len(triangles)):
            self.B[i] =  triangles[i].k.T @ triangles[i].grad_N
        self.nodes_conn = triangles.nodes_conn_table

    def calculate_elem_velocities(self, p, mu):
        p_vector = p[self.nodes_conn]
        v_array = -(1/mu) * np.einsum('ijk,ik->ij', self.B, p_vector) # not pretty
        return v_array
    
    def calculate_nodal_velocities(cls, nodes, v_array):
        v_nodal_array = []
        for node in nodes:
            supporting_triangle_velocities = v_array[node.triangle_ids]

            # Keep only rows where at least one velcity component is not 0
            mask = np.any(np.abs(supporting_triangle_velocities) != 0, axis=1)
            filtered_supporting_triangle_velocities = supporting_triangle_velocities[mask]

            if filtered_supporting_triangle_velocities.size > 0:
                avg_velocity = np.mean(filtered_supporting_triangle_velocities, 0)
            else:
                avg_velocity = np.zeros((3,))  # all empty elements

            v_nodal_array.append(avg_velocity.tolist())
        return v_nodal_array

    # TODO: numba jit compiled method version, currently unused
    # @njit
    # def _calculate_nodal_velocities_numba(triangle_id_lists, v_array):
    #     n_nodes = len(triangle_id_lists)
    #     v_nodal_array = np.zeros((n_nodes, 3))
    #
    #     for i in range(n_nodes):
    #         ids = triangle_id_lists[i]
    #         count = 0
    #         total = np.zeros(3)
    #
    #         for j in range(len(ids)):
    #             vel = v_array[ids[j]]
    #             if vel[0] != 0 or vel[1] != 0 or vel[2] != 0:
    #                 total += vel
    #                 count += 1
    #
    #         if count > 0:
    #             v_nodal_array[i] = total / count
    #         # else: remain as zeros
    #     return v_nodal_array
