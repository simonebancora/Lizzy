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
