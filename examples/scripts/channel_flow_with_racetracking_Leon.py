import lizzy as liz
from lizzy import SolverType

model = liz.LizzyModel()

model.read_mesh_file("../meshes/Rect_Type_1.msh")
model.assign_simulation_parameters(output_interval=10, fill_tolerance=0.01)

model.create_resin("resin", 0.145)
model.assign_resin("resin")

k = 4.6515E-10
model.create_material("domain_material", (k, k, k), 0.7, 0.003)
model.assign_material("domain_material", 'domain')

beta = 700

model.create_material("racetrack_material", (beta*k, beta*k, beta*k), 0.7, 0.003)
model.assign_material("racetrack_material", 'RT_top')
model.assign_material("racetrack_material", 'RT_bottom')

model.create_pressure_inlet("inlet", 70000)
model.assign_inlet("inlet", "inlet_zone")

model.create_vent("outlet", 0.0)
model.assign_vent("outlet", "outlet_zone")

model.initialise_solver(SolverType.ITERATIVE_PETSC)
solution = model.solve()

model.save_results(solution, "rect_with_RT_Leon")

