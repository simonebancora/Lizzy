import lizzy

model = lizzy.LizzyModel()
model.read_mesh_file("../meshes/Rect1M_R1.msh")
model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.01)

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 1.0)
model.assign_material("domain_material", 'domain')

model.create_inlet("inlet_left", 100000)
model.assign_inlet("inlet_left", "left_edge")

model.initialise_solver()
solution = model.solve()

model.save_results()