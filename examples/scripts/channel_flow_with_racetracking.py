import lizzy as liz
from lizzy import SolverType

model = liz.LizzyModel()

model.read_mesh_file("../meshes/Rect_with_RT.msh")
model.assign_simulation_parameters(wo_delta_time=10, fill_tolerance=0.01)

model.create_resin("resin", 0.1)
model.assign_resin("resin")

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.6, 1.0)
model.assign_material("domain_material", 'domain')

model.create_material("racetrack_material", (1E-8, 1E-8, 1E-8), 0.6, 1.0)
model.assign_material("racetrack_material", 'RT_top')
model.assign_material("racetrack_material", 'RT_bottom')

model.create_pressure_inlet("inlet", 100000)
model.assign_inlet("inlet", "inlet_zone")

model.create_vent("outlet", 0.0)
model.assign_vent("outlet", "outlet_zone")

model.initialise_solver(SolverType.ITERATIVE_PETSC)
solution = model.solve()

model.save_results(solution, "rect_with_RT")

