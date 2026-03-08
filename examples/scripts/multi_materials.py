import lizzy as liz

model = liz.LizzyModel()
model.read_mesh_file("../meshes/Triforce_R1.msh")
model.assign_simulation_parameters(output_interval=100)

model.create_resin("resin", 0.1)
model.assign_resin("resin")

model.create_material("high_perm_material", (1E-10, 1E-10, 1E-10), 0.5, 1.0, )
model.create_material("low_perm_material", (1E-13, 1E-13, 1E-13), 0.5, 1.0, )

model.assign_material("high_perm_material", 'background')
model.assign_material("low_perm_material", 'triforce')

model.create_pressure_inlet("inner_inlet", 1E+05)
model.assign_inlet("inner_inlet", "inner_rim")

model.initialise_solver()
model.solve()

model.save_results()