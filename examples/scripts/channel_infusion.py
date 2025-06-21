import lizzy as liz

model = liz.LizzyModel()

model.read_mesh_file("../meshes/Rect1M_R1.msh")

model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.01)

model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "pippo")
model.assign_material("pippo", 'domain')

model.create_sensor(0.2, 0.25, 0)

model.create_inlet(100000, "inlet_left")
model.assign_inlet("inlet_left", "left_edge")

model.initialise_solver()

solution = model.solve()

model.save_results(solution, "Rect1M_R1")