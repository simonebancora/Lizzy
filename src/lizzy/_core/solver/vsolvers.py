#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.datatypes.solverdata import SolverState
import numpy as np

class VelocitySolver:
    def __init__(self):
        self.darcy_operator = any
        self.nodes_conn = any
        self.flattened_node_ids = any
        self.n_tris_per_node_inverse_array = any

    def precalculate_darcy_operator_and_nodal_v_operator(self, triangles, tri_conn_table, node_idx_to_n_tris):
        """precalculate:
        - vectorised coefficient darcy_operator of shape function gradients for velocity: v = darcy_operator * p
        - array n_tris_per_node_inverse_array for velocity interpolation at nodes from surrounding elements
        """
        b_ncol = triangles[0].grad_N.shape[1]
        self.darcy_operator = np.empty((len(triangles), 3, b_ncol), dtype=float)
        for i in range(len(triangles)):
            self.darcy_operator[i] = triangles[i].k.T @ triangles[i].grad_N
        self.nodes_conn = tri_conn_table

        self.flattened_node_ids = tri_conn_table.reshape(-1)
        self.n_tris_per_node_inverse_array = (np.ones(len(node_idx_to_n_tris), dtype=float)/node_idx_to_n_tris).reshape(-1, 1)

    def update_velocities(self, state:SolverState):
        p = state.p_array
        mu = state.current_mu
        p_vector = p[self.nodes_conn]
        v_array = -(1/mu) * np.einsum('ijk,ik->ij', self.darcy_operator, p_vector) # not pretty
        state.v_array = v_array
        state.v_nodal_array = self._interpolate_velocities_to_nodes(len(state.p_array), v_array)
    
    def _interpolate_velocities_to_nodes(self, n_nodes: int, v_array: np.ndarray):
        v_nodal_array_undivided = np.zeros((n_nodes, 3), dtype=float)
        np.add.at(v_nodal_array_undivided, self.flattened_node_ids, np.repeat(v_array, 3, axis=0))
        return v_nodal_array_undivided * self.n_tris_per_node_inverse_array

    

