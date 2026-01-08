import lizzy as liz
import time

# Setup model
def setup_model():
    model = liz.LizzyModel()
    model.read_mesh_file("../meshes/Rect1M_R2.msh")
    model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.01)
    model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "domain_material")
    model.assign_material("domain_material", 'domain')
    model.create_sensor(0.2, 0.25, 0)
    model.create_inlet(100000, "inlet_left")
    model.assign_inlet("inlet_left", "left_edge")
    return model

# Test a solver
def test_solver(solver_type, name, **kwargs):
    print(f"\nTesting {name}...")
    model = setup_model()
    
    try:
        start = time.time()
        model.initialise_solver(solver_type=solver_type, **kwargs)
        model.solve()
        elapsed = time.time() - start
        print(f"  ✓ Success: {elapsed:.2f}s")
        return True, elapsed
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return False, None

# Define solvers to test
solvers = [
    (liz.SolverType.DIRECT_DENSE, "Direct Dense", {}),
    (liz.SolverType.DIRECT_SPARSE, "Direct Sparse", {}),
    (liz.SolverType.ITERATIVE_PETSC, "PETSc CG+GAMG", 
     {"solver_tol": 1e-8, "solver_max_iter": 1000, "ksp_type": "cg", "pc_type": "gamg"}),
    (liz.SolverType.ITERATIVE_PETSC, "PETSc GMRES+ILU", 
     {"solver_tol": 1e-8, "solver_max_iter": 1000, "ksp_type": "gmres", "pc_type": "ilu"}),
]

# Run tests
print("=" * 50)
print("Solver Comparison Test")
print("=" * 50)

results = []
for solver_type, name, kwargs in solvers:
    success, time_elapsed = test_solver(solver_type, name, **kwargs)
    if success:
        results.append((name, time_elapsed))

# Summary
print("\n" + "=" * 50)
print("Summary")
print("=" * 50)
if results:
    results.sort(key=lambda x: x[1])
    for i, (name, t) in enumerate(results, 1):
        print(f"{i}. {name}: {t:.2f}s")
else:
    print("No solvers succeeded")