import lizzy as liz

model = liz.LizzyModel()
model.read_mesh_file("../meshes/Triforce_R1.msh")
model.assign_simulation_parameters(mu=0.1, wo_delta_time=100)

model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "high_perm_material")
model.create_material(1E-13, 1E-13, 1E-13, 0.5, 1.0, "low_perm_material")

model.assign_material("high_perm_material", 'background')
model.assign_material("low_perm_material", 'triforce')


model.create_inlet(1E+05, "inner_inlet")
model.assign_inlet("inner_inlet", "inner_rim")

model.initialise_solver()
solution = model.solve()

model.save_results(solution, "Triforce")