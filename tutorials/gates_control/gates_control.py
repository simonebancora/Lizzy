import lizzy

# Set up logging level
import logging                                                                                                          
logging.basicConfig(level=logging.INFO)

# Set up the model: notice ``end_step_when_sensor_triggered=True`` because we want to use sensors to control the process.
model = lizzy.LizzyModel()
model.read_mesh_file("GatesControl.msh")
model.set_simulation_parameters(output_interval=10, progress_bar=False, end_step_when_sensor_triggered=True)

# Resin
model.create_resin("resin_01", 0.1)
model.assign_resin("resin_01")

# Materials
model.create_material("inlet_material", (1E-8, 1E-8, 1E-8), 0.5, 0.005)
model.assign_material("inlet_material", 'inlet')

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.005)
model.assign_material("domain_material", 'domain')

# Boundary conditions
model.create_pressure_inlet("inlet_1", 1E+05)
model.assign_inlet("inlet_1", "edge_1")

model.create_pressure_inlet("inlet_2", 1E+05)
model.assign_inlet("inlet_2", "edge_2")

model.create_pressure_inlet("inlet_3", 1E+05)
model.assign_inlet("inlet_3", "edge_3")

# Sensors
model.create_sensor("sensor_01", (0.36, 0.25, 0))
model.create_sensor("sensor_02", (0.71, 0.25, 0))

#Solver initialisation: this must be called before we can open or close inlets, or check sensor states.
model.initialise_solver()
model.close_inlet("inlet_2")
model.close_inlet("inlet_3")

# Start filling
while model.get_sensor_by_name("sensor_01").resin_arrived == False:
    model.solve_time_interval(10000)

# Resin has reached sensor_01, open the second inlet
model.open_inlet("inlet_2")
while model.get_sensor_by_name("sensor_02").resin_arrived == False:
    model.solve_time_interval(10000)

# Resin has reached sensor_02, open the third inlet
model.open_inlet("inlet_3")
model.solve()

# Save results
model.save_results()