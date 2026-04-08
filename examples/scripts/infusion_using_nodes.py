import lizzy

model = lizzy.LizzyModel()
model.read_mesh_file("../meshes/Rect1M_R1.msh")
model.set_simulation_parameters(output_interval=10)

model.create_resin("resin_01", 0.1)
model.assign_resin("resin_01")

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.01)
model.assign_material("domain_material", 'domain')

# Apply pressure at specific node IDs
model.assign_pressure_at_node(183, 100000)
model.assign_pressure_at_node(10, 100000)
model.assign_pressure_at_node(249, 50000)

model.initialise_solver()
model.solve()
model.save_results()