import lizzy

model = lizzy.LizzyModel()
model.read_mesh_file("../meshes/Rect1M_R1.msh")
model.assign_simulation_parameters(wo_delta_time=100)

model.create_resin("resin", 0.1)
model.assign_resin("resin")

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 1.0)
model.assign_material("domain_material", 'domain')

model.create_inlet("inlet_left", 100000)
model.assign_inlet("inlet_left", "left_edge")

model.initialise_solver()
model.solve()

model.save_results()