"""
Solver Comparison Example
=========================

This example demonstrates how to use different solvers available in Lizzy.
The same filling simulation is run with three different solver types to 
compare their results.

Available solvers:
- DIRECT_SPARSE: Direct solver using sparse matrix factorization (recommended for small/medium meshes)
- DIRECT_DENSE: Direct solver using dense matrices (only for very small problems)
- ITERATIVE_PETSC: Iterative solver using PETSc library (recommended for large meshes)
"""

import time
import lizzy as liz

# =============================================================================
# Model Setup (common for all solvers)
# =============================================================================

# Read mesh
model = liz.LizzyModel()
model.read_mesh_file("../meshes/Rect1M_R1.msh")

# Set simulation parameters
model.assign_simulation_parameters(
    wo_delta_time=100,   # Initial time step guess [s]
    fill_tolerance=0.00  # Fill fraction tolerance for CV to be considered full
)

# Create and assign resin
model.create_resin("resin", 0.1) # Resin viscosity 0.1 [Pa.s]
model.assign_resin("resin")

# Create and assign material
model.create_material(
    "glass_fiber",             # Material name
    (1e-10, 1e-10, 1e-10),     # Permeability (k1, k2, k3) [m^2]
    0.5,                       # Porosity [-]
    1.0                       # Thickness [m]
)
model.assign_material("glass_fiber", "domain")

# Create inlet with prescribed pressure
model.create_inlet("left_inlet", 1e5)  # 1 bar
model.assign_inlet("left_inlet", "left_edge")

# =============================================================================
# Example 1: Direct Sparse Solver (default, recommended)
# =============================================================================
print("\n" + "="*60)
print("Running with DIRECT_SPARSE solver")
print("="*60)

model.initialise_solver(solver_type=liz.SolverType.DIRECT_SPARSE)
start_time = time.time()
solution_sparse = model.solve()
time_sparse = time.time() - start_time

print(f"Fill time: {solution_sparse.time[-1]:.2f} s")
print(f"Number of time steps: {len(solution_sparse.time)}")
print(f"Solver runtime: {time_sparse:.2f} s")

# =============================================================================
# Example 2: Direct Dense Solver (for comparison only - slow for large meshes)
# =============================================================================
print("\n" + "="*60)
print("Running with DIRECT_DENSE solver")
print("="*60)

model.initialise_solver(solver_type=liz.SolverType.DIRECT_DENSE)
start_time = time.time()
solution_dense = model.solve()
time_dense = time.time() - start_time

print(f"Fill time: {solution_dense.time[-1]:.2f} s")
print(f"Number of time steps: {len(solution_dense.time)}")
print(f"Solver runtime: {time_dense:.2f} s")

# =============================================================================
# Example 3: Iterative PETSc Solver (best for large meshes)
# =============================================================================
print("\n" + "="*60)
print("Running with ITERATIVE_PETSC solver")
print("="*60)

model.initialise_solver(
    solver_type=liz.SolverType.ITERATIVE_PETSC,
    solver_tol=1e-6,       # Solver tolerance
    solver_max_iter=1000,  # Maximum iterations
    ksp_type="cg",         # Conjugate gradient method
    pc_type="gamg"         # Algebraic multigrid preconditioner
)
start_time = time.time()
solution_petsc = model.solve()
time_petsc = time.time() - start_time

print(f"Fill time: {solution_petsc.time[-1]:.2f} s")
print(f"Number of time steps: {len(solution_petsc.time)}")
print(f"Solver runtime: {time_petsc:.2f} s")

# =============================================================================
# Compare Results
# =============================================================================
print("\n" + "="*60)
print("Results Comparison")
print("="*60)
print(f"{'Solver':<20} {'Fill Time [s]':<15} {'Runtime [s]':<15}")
print("-"*50)
print(f"{'DIRECT_SPARSE':<20} {solution_sparse.time[-1]:<15.4f} {time_sparse:<15.2f}")
print(f"{'DIRECT_DENSE':<20} {solution_dense.time[-1]:<15.4f} {time_dense:<15.2f}")
print(f"{'ITERATIVE_PETSC':<20} {solution_petsc.time[-1]:<15.4f} {time_petsc:<15.2f}")

# Save results from one of the solutions
model.save_results(solution_sparse, "solver_comparison")
