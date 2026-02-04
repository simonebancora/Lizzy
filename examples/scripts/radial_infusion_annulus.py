import lizzy as liz
from lizzy import SolverType

model = liz.LizzyModel()

model.read_mesh_file("../meshes/quarter_annulus.msh")
model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.00)

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.6, 1.0)
model.assign_material("domain_material", 'domain')

model.create_inlet("inner_radius", 100000)
model.assign_inlet("inner_radius", "inlet")

model.initialise_solver(SolverType.ITERATIVE_PETSC)
solution = model.solve()

model.save_results(solution, "quarter_annulus")

# Lee, Y. M., et al. "Analysis of flow in the RTM Process." SAE transactions (1989): 65-75.
# Eq. (A-4) : 
# r_0 = 1, r_m = 2, phi = 0.6, eta = 0.1, K = 1e-10, P0 = 1e5
# Then the filling time = 3817.77 seconds