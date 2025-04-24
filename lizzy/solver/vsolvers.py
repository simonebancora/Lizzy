#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

class VelocitySolver:
    B = any
    nodes_conn = any

    @classmethod
    def precalculate_B(cls, triangles):

        b_ncol = triangles[0].grad_N.shape[1]
        cls.B = np.empty((len(triangles), 3, b_ncol), dtype=object)

        for i in range(len(triangles)):
            cls.B[i] =  triangles[i].k.T @ triangles[i].grad_N
        cls.nodes_conn = triangles.nodes_conn_table

    @classmethod
    def calculate_elem_velocities(cls, p, mu):
        p_vector = p[cls.nodes_conn]
        v_array = -(1/mu) * np.einsum('ijk,ik->ij', cls.B, p_vector) # not pretty
        return v_array
    
    @classmethod
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
