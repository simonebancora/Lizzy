import lizzy as liz
import time

model = liz.LizzyModel()

model.read_mesh_file("../meshes/Rect1M_R1.msh")

model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.01)

model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "pippo")
model.assign_material("pippo", 'domain')

model.create_sensor(0.1, 0.05, 0)

model.create_inlet(100000, "inlet")
model.assign_inlet("inlet", "left_edge")

start = time.time()
model.initialise_solver()
while model.n_empty_cvs > 0:
    solution = model.solve_step(10)
end = time.time()

print(end - start)
