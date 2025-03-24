#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

def Assembly(mesh, mu):
    K_tri = np.zeros((mesh.nodes.N, mesh.nodes.N))
    f = np.zeros((mesh.nodes.N,))

    for tri in mesh.triangles:
        k_el = tri.grad_N.T @ tri.k @ tri.grad_N * tri.A * tri.h / mu
        for i in range(3):
            for j in range(3):
                K_tri[tri.node_ids[i], tri.node_ids[j]] += k_el[i, j]
                
    return K_tri, f


