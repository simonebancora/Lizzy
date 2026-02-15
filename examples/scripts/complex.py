import lizzy as liz

model = liz.LizzyModel()
model.read_mesh_file("../meshes/Complex_rotated.msh")
model.assign_simulation_parameters(wo_delta_time=100, fill_tolerance=0.01)

model.create_resin("resin", 0.1)
model.assign_resin("resin")

model.create_material("material_iso", (1E-10, 1E-10, 1E-10), 0.5, 1.0, )
model.create_material("material_aniso", (1E-10, 1E-11, 1E-11), 0.5, 1.0, )
model.create_material("material_racetrack", (1E-7, 1E-7, 1E-7), 0.5, 0.5, )

rosette_ramp = model.create_rosette("rosette_ramp", (model._mesh.nodes[12].coords - model._mesh.nodes[13].coords) )
model.assign_material("material_iso", 'Lshape')
model.assign_material("material_aniso", 'ramp', rosette_ramp)
model.assign_material("material_racetrack", 'racetrack')

model.create_pressure_inlet("inlet_left", 100000)
model.assign_inlet("inlet_left", "inlet")

model.initialise_solver()
model.solve()

model.save_results()

