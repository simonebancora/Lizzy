#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.datatypes.solverstate import SolverState
import numpy as np


class VelocitySolver:
    def __init__(self, triangles):
        self.darcy_operator = any
        self.nodes_conn = any

    def precalculate_darcy_operator(self, triangles, tri_conn_table):
        """precalculate vectorised coefficient darcy_operator of shape function gradients for velocity: v = darcy_operator * p"""
        b_ncol = triangles[0].grad_N.shape[1]
        self.darcy_operator = np.empty((len(triangles), 3, b_ncol), dtype=float)
        for i in range(len(triangles)):
            self.darcy_operator[i] = triangles[i].k.T @ triangles[i].grad_N
        self.nodes_conn = tri_conn_table

    def update_elem_velocities(self, state:SolverState):
        p = state.p_array
        mu = state.current_mu
        p_vector = p[self.nodes_conn]
        v_array = -(1/mu) * np.einsum('ijk,ik->ij', self.darcy_operator, p_vector) # not pretty
        state.v_array = v_array
