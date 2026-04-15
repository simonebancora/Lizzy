import lizzy

# Set up logging level
import logging                                                                                                          
logging.basicConfig(level=logging.INFO)

# Set up the model: save results every 30 seconds of process time
model = lizzy.LizzyModel()
model.read_mesh_file("ChannelFlow.msh")
model.set_simulation_parameters(output_interval=30, progress_bar=True)

# Create a resin and assign it
model.create_resin("resin_01", 0.1)
model.assign_resin("resin_01")

# Create a material and assign it to the domain
model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.005)
model.assign_material("domain_material", 'domain')

# Boundary conditions
model.create_pressure_inlet("inlet_left", 1E+05)
model.assign_inlet("inlet_left", "left_edge")

model.create_vent("vent_right", 0.0)
model.assign_vent("vent_right", "right_edge")

# Solve
model.initialise_solver()
model.solve()

# Save results
model.save_results()