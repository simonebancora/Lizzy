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

# Test a solver configuration
def test_solver_config(solver_type, use_masked, name, **kwargs):
    print(f"\nTesting {name}...")
    model = setup_model()
    
    try:
        start = time.time()
        model.initialise_solver(solver_type=solver_type, use_masked_solver=use_masked, **kwargs)
        solution = model.solve()
        elapsed = time.time() - start
        print(f"  ✓ Success: {elapsed:.2f}s")
        print(f"    - Fill time: {solution.time[-1]:.5f}s")
        return True, elapsed, solution
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

# Define solver configurations to test
solver_configs = [
    (liz.SolverType.ITERATIVE_PETSC, True, "Masked Solver (PETSc CG+GAMG)", {"solver_tol": 1e-4, "solver_max_iter": 1000, "ksp_type": "cg", "pc_type": "gamg"}),
    (liz.SolverType.ITERATIVE_PETSC, True, "Masked Solver (PETSc GMRES+ILU)", {"solver_tol": 1e-4, "solver_max_iter": 1000, "ksp_type": "gmres", "pc_type": "ilu"}),
    (liz.SolverType.DIRECT_SPARSE, True, "Masked Solver (DIRECT_SPARSE)", {}),
    (liz.SolverType.DIRECT_DENSE, True, "Masked Solver (DIRECT_DENSE)", {}),
    (liz.SolverType.DIRECT_SPARSE, False, "Traditional Solver (DIRECT_SPARSE)", {}),
]

# Run tests
print("=" * 70)
print("Solver Performance Comparison: Traditional vs Masked (Optimized)")
print("=" * 70)

results = []
baseline_time = None

for solver_type, use_masked, name, kwargs in solver_configs:
    success, time_elapsed, solution = test_solver_config(solver_type, use_masked, name, **kwargs)
    if success:
        # Store baseline time from traditional solver
        if not use_masked and baseline_time is None:
            baseline_time = time_elapsed
        
        results.append((name, time_elapsed, use_masked))

# Summary
print("\n" + "=" * 70)
print("Performance Summary")
print("=" * 70)

if results:
    # Sort by time
    results.sort(key=lambda x: x[1])
    
    print(f"\n{'Rank':<6} {'Solver Configuration':<45} {'Time (s)':<12} {'Speedup':<10}")
    print("-" * 70)
    
    for i, (name, t, is_masked) in enumerate(results, 1):
        if baseline_time and baseline_time > 0:
            speedup = baseline_time / t
            speedup_str = f"{speedup:.2f}x"
        else:
            speedup_str = "N/A"
        
        marker = "🚀" if is_masked else "📊"
        print(f"{i:<6} {marker} {name:<43} {t:<12.2f} {speedup_str:<10}")
    
    # Highlight the winner
    if len(results) > 1:
        winner_name, winner_time, winner_masked = results[0]
        print("\n" + "=" * 70)
        print(f"🏆 Fastest: {winner_name}")
        if baseline_time and winner_masked:
            improvement = ((baseline_time - winner_time) / baseline_time) * 100
            print(f"   Performance improvement over traditional: {improvement:.1f}%")
        print("=" * 70)
else:
    print("No solvers succeeded")

print("\nLegend:")
print("  📊 = Traditional solver (full matrix)")
print("  🚀 = Masked/optimized solver (submatrix extraction)")
