import lizzy


model = lizzy.LizzyModel()
model.read_mesh_file("../meshes/Rect1M_R2.msh")
model.assign_simulation_parameters(wo_delta_time=10)


model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.01)
model.assign_material("domain_material", 'domain')

model.create_pressure_inlet("inlet_left", 100000)
model.assign_inlet("inlet_left", "left_edge")

# model.create_flowrate_inlet("inlet_fr_left", 0.000001)
# model.assign_inlet("inlet_fr_left", "left_edge")

model.initialise_solver()
model.solve()

model.save_results()