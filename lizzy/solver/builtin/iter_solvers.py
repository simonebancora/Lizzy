#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import cg, bicgstab, gmres
import warnings

# Optional imports with availability checks
try:
    import pyamg
    PYAMG_AVAILABLE = True
except ImportError:
    PYAMG_AVAILABLE = False

try:
    import petsc4py
    petsc4py.init()
    from petsc4py import PETSc
    PETSC_AVAILABLE = True
except ImportError:
    PETSC_AVAILABLE = False


def solve_pressure_cg(k: np.ndarray, f: np.ndarray, tol: float = 1e-8, max_iter: int = 1000):
    """
    Solve pressure system using Conjugate Gradient method.
    
    Parameters
    ----------
    k : np.ndarray
        Stiffness matrix (will be converted to sparse if not already)
    f : np.ndarray
        Right-hand side vector
    tol : float
        Convergence tolerance
    max_iter : int
        Maximum number of iterations
        
    Returns
    -------
    np.ndarray
        Solution vector
    """
    if not isinstance(k, csr_matrix):
        k_sparse = csr_matrix(k)
    else:
        k_sparse = k
    
    p, info = cg(k_sparse, f, rtol=tol, maxiter=max_iter)
    
    if info > 0:
        warnings.warn(f"CG solver did not converge after {info} iterations")
    elif info < 0:
        raise RuntimeError(f"CG solver failed with error code {info}")
    
    return p


def solve_pressure_bicgstab(k: np.ndarray, f: np.ndarray, tol: float = 1e-8, max_iter: int = 1000):
    """
    Solve pressure system using BiCGSTAB method.
    
    Parameters
    ----------
    k : np.ndarray
        Stiffness matrix (will be converted to sparse if not already)
    f : np.ndarray
        Right-hand side vector
    tol : float
        Convergence tolerance
    max_iter : int
        Maximum number of iterations
        
    Returns
    -------
    np.ndarray
        Solution vector
    """
    if not isinstance(k, csr_matrix):
        k_sparse = csr_matrix(k)
    else:
        k_sparse = k
    
    p, info = bicgstab(k_sparse, f, rtol=tol, maxiter=max_iter)
    
    if info > 0:
        warnings.warn(f"BiCGSTAB solver did not converge after {info} iterations")
    elif info < 0:
        raise RuntimeError(f"BiCGSTAB solver failed with error code {info}")
    
    return p


def solve_pressure_gmres(k: np.ndarray, f: np.ndarray, tol: float = 1e-8, max_iter: int = 1000):
    """
    Solve pressure system using GMRES method.
    
    Parameters
    ----------
    k : np.ndarray
        Stiffness matrix (will be converted to sparse if not already)
    f : np.ndarray
        Right-hand side vector
    tol : float
        Convergence tolerance
    max_iter : int
        Maximum number of iterations
        
    Returns
    -------
    np.ndarray
        Solution vector
    """
    if not isinstance(k, csr_matrix):
        k_sparse = csr_matrix(k)
    else:
        k_sparse = k
    
    p, info = gmres(k_sparse, f, rtol=tol, maxiter=max_iter)
    
    if info > 0:
        warnings.warn(f"GMRES solver did not converge after {info} iterations")
    elif info < 0:
        raise RuntimeError(f"GMRES solver failed with error code {info}")
    
    return p


def solve_pressure_pyamg(k: np.ndarray, f: np.ndarray, tol: float = 1e-8, max_iter: int = 1000, 
                        accel: str = 'cg', cycle: str = 'V', verbose: bool = False):
    """
    Solve pressure system using PyAMG algebraic multigrid method.
    
    Parameters
    ----------
    k : np.ndarray
        Stiffness matrix (will be converted to sparse if not already)
    f : np.ndarray
        Right-hand side vector
    tol : float
        Convergence tolerance
    max_iter : int
        Maximum number of iterations
    accel : str
        Acceleration method ('cg', 'gmres', 'fgmres', or None)
    cycle : str
        Multigrid cycle type ('V', 'W', 'F')
    verbose : bool
        Whether to print convergence information
        
    Returns
    -------
    np.ndarray
        Solution vector
    """
    if not PYAMG_AVAILABLE:
        raise ImportError("PyAMG is not available. Install it with: pip install pyamg")
    
    if not isinstance(k, csr_matrix):
        k_sparse = csr_matrix(k)
    else:
        k_sparse = k
    
    # Create AMG hierarchy
    ml = pyamg.smoothed_aggregation_solver(k_sparse)
    
    # Solve using AMG with residual tracking
    residuals = []
    p = ml.solve(f, tol=tol, maxiter=max_iter, accel=accel, cycle=cycle, residuals=residuals)
    
    if verbose and len(residuals) > 0:
        print(f"PyAMG converged in {len(residuals)} iterations")
        print(f"Final residual: {residuals[-1]:.2e}")
    
    return p


def solve_pressure_petsc(k: np.ndarray, f: np.ndarray, tol: float = 1e-8, max_iter: int = 1000,
                        ksp_type: str = 'cg', pc_type: str = 'gamg', verbose: bool = False):
    """
    Solve pressure system using PETSc solvers with AMG preconditioning.
    
    Parameters
    ----------
    k : np.ndarray
        Stiffness matrix (will be converted to sparse if not already)
    f : np.ndarray
        Right-hand side vector
    tol : float
        Convergence tolerance
    max_iter : int
        Maximum number of iterations
    ksp_type : str
        KSP solver type ('cg', 'gmres', 'bicg', etc.)
    pc_type : str
        Preconditioner type ('gamg', 'hypre', 'ilu', etc.)
    verbose : bool
        Whether to print convergence information
        
    Returns
    -------
    np.ndarray
        Solution vector
    """
    if not PETSC_AVAILABLE:
        raise ImportError("PETSc is not available. Install it with: pip install petsc petsc4py")
    
    if not isinstance(k, csr_matrix):
        k_sparse = csr_matrix(k)
    else:
        k_sparse = k
    
    # Convert to PETSc format
    A = PETSc.Mat().createAIJ(size=k_sparse.shape, 
                              csr=(k_sparse.indptr, k_sparse.indices, k_sparse.data))
    b = PETSc.Vec().createWithArray(f)
    x = PETSc.Vec().createWithArray(np.zeros_like(f))
    
    # Set up the KSP solver
    ksp = PETSc.KSP().create()
    ksp.setOperators(A)
    
    # Set up preconditioner
    pc = ksp.getPC()
    pc.setType(pc_type)
    
    # Set solver parameters
    ksp.setTolerances(rtol=tol, max_it=max_iter)
    ksp.setType(ksp_type)
    
    # Solve the system
    ksp.solve(b, x)
    
    if verbose:
        print(f"PETSc solver converged in {ksp.getIterationNumber()} iterations "
              f"to a tolerance of {ksp.getResidualNorm():.2e}")
    
    # Convert solution back to numpy array
    solution = x.getArray().copy()
    
    # Clean up PETSc objects
    A.destroy()
    b.destroy()
    x.destroy()
    ksp.destroy()
    
    return solution