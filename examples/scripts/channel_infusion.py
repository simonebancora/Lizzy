import lizzy


model = lizzy.LizzyModel()
model.read_mesh_file("../meshes/Rect1M_R2.msh")
model.assign_simulation_parameters(output_interval=10)

model.create_resin("resin_01", 0.1)
model.assign_resin("resin_01")

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.01)
model.assign_material("domain_material", 'domain')

model.create_pressure_inlet("inlet_left", 100000)
model.assign_inlet("inlet_left", "left_edge")

model.create_vent("vent_right", vacuum_pressure=10.0)
model.assign_vent("vent_right", "right_edge")


model.initialise_solver()

model.solve()

model.save_results()