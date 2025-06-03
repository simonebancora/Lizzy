import lizzy as liz

model = liz.LizzyModel()

model.read_mesh_file("../meshes/Rect1M_R1.msh")

material = model.create_porous_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "pippo")
model.assign_material(material, 'domain')

model.create_sensor(0.1, 0.05, 0)

inlet = liz.create_inlet(100000)
model.assign_inlet(inlet, "left_edge")

model.initialise_solver()

solution = model.solve_step(10)

model.get_sensor_readings()

solution = model.solve_step(40)

model.get_sensor_readings()

solution = model.solve_step(100)

model.get_sensor_readings()
