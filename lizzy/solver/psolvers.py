#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from enum import Enum, auto
from lizzy.solver.builtin.direct_solvers import *
from lizzy.solver.builtin.iter_solvers import *
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt


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

        # # apply bcs
        # k_modified[dirichlet_idx_full, :] = 0
        # k_modified[dirichlet_idx_full, dirichlet_idx_full] = 1
        # f_modified[dirichlet_idx_full] = dirichlet_vals_full

        # return k_modified, f_modified

        # Eliminate Dirichlet DOFs symmetrically
        for idx, val in zip(dirichlet_idx_full, dirichlet_vals_full):
            f_modified -= k_modified[:, idx] * val
            k_modified[:, idx] = 0
            k_modified[idx, :] = 0
            k_modified[idx, idx] = 1
            f_modified[idx] = val

        return k_modified, f_modified


    @staticmethod
    def apply_starting_bcs(k, f, bcs):
        dirichlet_idx_full = np.concatenate((bcs.dirichlet_idx, bcs.p0_idx), axis=None)
        dirichlet_vals_full = np.concatenate((bcs.dirichlet_vals, np.zeros((1, len(bcs.p0_idx)))), axis=None)

        k_modified = k.copy()
        f_modified = f.copy()



        #
        # # apply bcs
        # k_modified[dirichlet_idx_full, :] = 0
        # k_modified[dirichlet_idx_full, dirichlet_idx_full] = 1
        # f_modified[dirichlet_idx_full] = dirichlet_vals_full
        #
        # # at this point, this is a diagonal identity matrix
        #
        # return k_modified, f_modified


        for idx, val in zip(dirichlet_idx_full, dirichlet_vals_full):
            f_modified -= k_modified[:, idx] * val
            k_modified[:, idx] = 0
            k_modified[idx, :] = 0
            k_modified[idx, idx] = 1
            f_modified[idx] = val

        return k_modified, f_modified

    @staticmethod
    def free_dofs(k_sol, f_sol, k_sing, f_orig, new_dofs):
        for dof in new_dofs:
            k_sol[dof, :] = k_sing[dof, :]
            k_sol[:, dof] = k_sing[:, dof]
            f_sol[dof] = f_orig[dof]
        plt.spy(k_sol, markersize=1)
        plt.show()
        return k_sol, f_sol

    # @staticmethod
    # def NEW_solve(k, f, bcs):
    #     dirichlet_idx_full = np.concatenate((bcs.dirichlet_idx, bcs.p0_idx), axis=None)
    #     dirichlet_vals_full = np.concatenate((bcs.dirichlet_vals, np.zeros((1, len(bcs.p0_idx)))), axis=None)
    #
    #     all_idx = np.arange(k.shape[0])
    #     free_idx = np.setdiff1d(all_idx, dirichlet_idx_full)
    #
    #     # Adjust right-hand side for known Dirichlet values
    #     f_mod = f[free_idx] - k[np.ix_(free_idx, dirichlet_idx_full)] @ dirichlet_vals_full
    #
    #     # Remove rows and columns from stiffness matrix
    #     k_mod = k[np.ix_(free_idx, free_idx)]
    #
    #     # p_reduced = np.linalg.solve(k_mod, f_mod)
    #
    #     p_reduced, info = cg(k_mod, f_mod)
    #
    #
    #     p_full = np.zeros_like(f)
    #     p_full[free_idx] = p_reduced
    #     p_full[dirichlet_idx_full] = dirichlet_vals_full
    #
    #     return p_full






