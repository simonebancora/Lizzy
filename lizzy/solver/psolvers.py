#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from enum import Enum, auto
from lizzy.solver.builtin.direct_solvers import *

class SolverType(Enum):
    DIRECT_DENSE = auto()
    DIRECT_SPARSE = auto()

class PressureSolver:
    @staticmethod
    def solve(k:np.ndarray, f:np.ndarray, method:SolverType = SolverType.DIRECT_SPARSE):
        """
        Solve the system `K p = f`.

        Parameters
        ----------
        k : np.ndarray
            Stiffness matrix with Dirichlet BCs applied by row/column method. Dimension (N,N) where N is the number of Dofs (1 per node)
        f : np.ndarray
            Right-hand side vector. Zeros (no source yet) with ones in Dirichlet nodes. Dimension (N,1)
        method : SolverType
            The solver type to be used. Default is SPARSE.
        """
        match method:
            case SolverType.DIRECT_DENSE:
                p = solve_pressure_direct_dense(k, f)
            case SolverType.DIRECT_SPARSE:
                p = solve_pressure_direct_sparse(k, f)
            case _:
                raise ValueError(f"Unknown solver type: {method}")
        return p

    @staticmethod
    def apply_bcs(k, f, bcs):
        dirichlet_idx_full = np.concatenate((bcs.dirichlet_idx, bcs.p0_idx), axis=None)
        dirichlet_vals_full = np.concatenate((bcs.dirichlet_vals, np.zeros((1, len(bcs.p0_idx)))), axis=None)

        k_modified = k.copy()
        f_modified = f.copy()

        # apply bcs
        for i, node_id in enumerate(dirichlet_idx_full):
            k_modified[node_id, :] = 0
            k_modified[node_id, node_id] = 1
            f_modified[node_id] = dirichlet_vals_full[i]
        return k_modified, f_modified





