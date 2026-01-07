#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from enum import Enum, auto
from .builtin.direct_solvers import solve_pressure_direct_dense, solve_pressure_direct_sparse
from .builtin.iter_solvers import solve_pressure_petsc
from scipy.sparse import csr_matrix, issparse

class SolverType(Enum):
    """
    Enum representing the available pressure solver types.

    Parameters
    ----------
    DIRECT_DENSE : SolverType
        Direct solver using dense matrix factorization.
    DIRECT_SPARSE : SolverType
        Direct solver using sparse matrix factorization.
    ITERATIVE_PETSC : SolverType
        Iterative solver using PETSc.
    """
    DIRECT_DENSE = auto()
    DIRECT_SPARSE = auto()
    ITERATIVE_PETSC = auto()

class PressureSolver:
    @staticmethod
    def solve(k:np.ndarray, f:np.ndarray, method:SolverType = SolverType.DIRECT_SPARSE, 
              tol:float = 1e-8, max_iter:int = 1000, verbose:bool = False, **solver_kwargs):
        """
        Solve the system `K p = f`.

        Parameters
        ----------
        k : np.ndarray
            Stiffness matrix with Dirichlet BCs applied by row/column method. Dimension (N,N) where N is the number of Dofs (1 per node)
        f : np.ndarray
            Right-hand side vector. Zeros (no source yet) with ones in Dirichlet nodes. Dimension (N,1)
        method : SolverType
            The solver type to be used. Default is DIRECT_SPARSE.
        tol : float
            Convergence tolerance for iterative solvers. Default is 1e-8.
        max_iter : int
            Maximum number of iterations for iterative solvers. Default is 1000.
        verbose : bool
            Whether to print convergence information for iterative solvers. Default is False.
        **solver_kwargs
            Additional keyword arguments passed to specific solvers.
        """
        match method:
            case SolverType.DIRECT_DENSE:
                p = solve_pressure_direct_dense(k, f)
            case SolverType.DIRECT_SPARSE:
                p = solve_pressure_direct_sparse(k, f)
            case SolverType.ITERATIVE_PETSC:
                # Extract PETSc specific parameters
                ksp_type = solver_kwargs.get('ksp_type', 'cg')
                pc_type = solver_kwargs.get('pc_type', 'gamg')
                p = solve_pressure_petsc(k, f, tol=tol, max_iter=max_iter,
                                       ksp_type=ksp_type, pc_type=pc_type, verbose=verbose)
            case _:
                raise ValueError(f"Unknown solver type: {method}")
        return p

    @staticmethod
    def apply_bcs(k, f, bcs):
        """
        Apply boundary conditions using symmetric elimination (traditional method).
        
        Note: This method modifies the entire matrix for each BC, which is inefficient
        for filling simulations. Consider using solve_with_mask() instead for better performance.
        """
        dirichlet_idx_full = np.concatenate((bcs.dirichlet_idx, bcs.p0_idx), axis=None)
        dirichlet_vals_full = np.concatenate((bcs.dirichlet_vals, np.zeros(len(bcs.p0_idx))), axis=None)

        # Convert to dense if sparse (traditional solver works better with dense for BC application)
        if issparse(k):
            k_modified = k.toarray()
        else:
            k_modified = k.copy()
            
        f_modified = f.copy()

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
        """Apply boundary conditions at the start (legacy method)."""
        dirichlet_idx_full = np.concatenate((bcs.dirichlet_idx, bcs.p0_idx), axis=None)
        dirichlet_vals_full = np.concatenate((bcs.dirichlet_vals, np.zeros(len(bcs.p0_idx))), axis=None)

        # Convert to dense if sparse
        if issparse(k):
            k_modified = k.toarray()
        else:
            k_modified = k.copy()
            
        f_modified = f.copy()

        for idx, val in zip(dirichlet_idx_full, dirichlet_vals_full):
            f_modified -= k_modified[:, idx] * val
            k_modified[:, idx] = 0
            k_modified[idx, :] = 0
            k_modified[idx, idx] = 1
            f_modified[idx] = val

        return k_modified, f_modified

    @staticmethod
    def solve_with_mask(k_original, f_original, bcs, method:SolverType = SolverType.DIRECT_SPARSE,
                       tol:float = 1e-8, max_iter:int = 1000, verbose:bool = False, **solver_kwargs):
        """
        Optimized solver that extracts and solves only the free DOFs (submatrix approach).
        
        This is much faster than the traditional approach, especially in early timesteps
        where most nodes are either filled (known p) or empty (p=0).
        
        Performance: For a mesh with 5% active DOFs, this is ~10-400x faster than 
        solving the full system.
        
        Parameters
        ----------
        k_original : np.ndarray or sparse matrix
            Original (unmodified) stiffness matrix
        f_original : np.ndarray
            Original (unmodified) force vector
        bcs : SolverBCs
            Boundary conditions object containing dirichlet_idx, dirichlet_vals, and p0_idx
        method : SolverType
            The solver type to use for the reduced system
        tol : float
            Convergence tolerance for iterative solvers
        max_iter : int
            Maximum iterations for iterative solvers
        verbose : bool
            Print solver information
        **solver_kwargs
            Additional solver-specific arguments
            
        Returns
        -------
        np.ndarray
            Full pressure solution vector with all DOFs
        """
        # Combine all Dirichlet DOFs (inlet pressures + empty node p=0 conditions)
        dirichlet_idx = np.concatenate([bcs.dirichlet_idx, bcs.p0_idx])
        dirichlet_vals = np.concatenate([bcs.dirichlet_vals, np.zeros(len(bcs.p0_idx))])
        
        # Identify free DOFs (unknowns to solve for)
        N = k_original.shape[0]
        all_dofs = np.arange(N)
        free_dofs = np.setdiff1d(all_dofs, dirichlet_idx)
        
        # If all DOFs are constrained, return the constrained values
        if len(free_dofs) == 0:
            p_full = np.zeros(N)
            p_full[dirichlet_idx] = dirichlet_vals
            return p_full
        
        # Extract submatrix for free DOFs only
        K_free = k_original[np.ix_(free_dofs, free_dofs)]
        K_constrained = k_original[np.ix_(free_dofs, dirichlet_idx)]
        
        # Modify RHS to account for known Dirichlet values
        if issparse(K_constrained):
            f_free = f_original[free_dofs] - K_constrained.dot(dirichlet_vals)
        else:
            f_free = f_original[free_dofs] - K_constrained @ dirichlet_vals
        
        # Convert to dense if using DIRECT_DENSE solver and matrix is sparse
        if method == SolverType.DIRECT_DENSE and issparse(K_free):
            K_free = K_free.toarray()
        
        # Solve the reduced system (much smaller!)
        p_free = PressureSolver.solve(K_free, f_free, method, tol=tol, 
                                     max_iter=max_iter, verbose=verbose, **solver_kwargs)
        
        # Reconstruct full solution vector
        p_full = np.zeros(N)
        p_full[free_dofs] = p_free
        p_full[dirichlet_idx] = dirichlet_vals
        
        return p_full

    @staticmethod
    def free_dofs(k_sol, f_sol, k_sing, f_orig, new_dofs):
        for dof in new_dofs:
            k_sol[dof, :] = k_sing[dof, :]
            k_sol[:, dof] = k_sing[:, dof]
            f_sol[dof] = f_orig[dof]
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






