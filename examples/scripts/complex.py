import lizzy as liz

model = liz.LizzyModel()
model.read_mesh_file("../meshes/Complex_rotated.msh")
model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.01)
model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "material_iso")
model.create_material(1E-10, 1E-11, 1E-11, 0.5, 1.0, "material_aniso")
model.create_material(1E-7, 1E-7, 1E-7, 0.5, 0.5, "material_racetrack")
rosette_ramp = liz.Rosette(model._mesh.nodes[12].coords, model._mesh.nodes[13].coords)
model.assign_material("material_iso", 'Lshape')
model.assign_material("material_aniso", 'ramp', rosette_ramp)
model.assign_material("material_racetrack", 'racetrack')


model.create_inlet(100000, "inlet_left")
model.assign_inlet("inlet_left", "inlet")

model.initialise_solver()
solution = model.solve()
model.save_results(solution, "Complex_rotated")

