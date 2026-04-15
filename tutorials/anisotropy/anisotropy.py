import lizzy

# Set up logging level
import logging
logging.basicConfig(level=logging.INFO)

# Set up the model: save results every 60 seconds of process time
model = lizzy.LizzyModel()
model.read_mesh_file("Anisotropy.msh")
model.set_simulation_parameters(output_interval=60, progress_bar=True)

# Create a resin and assign it
model.create_resin("resin", 0.1)
model.assign_resin("resin")

# Create an anisotropic material, an orientation rosette and assign both to the domain
model.create_rosette("rosette", (1,1,0))
model.create_material("aniso_material", (1E-10, 1E-11, 1E-10), 0.5, 0.005)
model.assign_material("aniso_material", 'domain', "rosette")

# Boundary conditions
model.create_pressure_inlet("inner_inlet", 1E+05)
model.assign_inlet("inner_inlet", "inner_rim")

model.create_vent("outer_vent", 0.0)
model.assign_vent("outer_vent", "outer_rim")

# Solve
model.initialise_solver()
model.solve()

# Save results
model.save_results()