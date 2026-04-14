import lizzy

import logging
logging.basicConfig(level=logging.INFO)

model = lizzy.LizzyModel()
model.read_mesh_file("Anisotropy.msh")
model.set_simulation_parameters(output_interval=60, progress_bar=True)

model.create_resin("resin", 0.1)
model.assign_resin("resin")

model.create_rosette("rosette", (1,1,0))
model.create_material("aniso_material", (1E-10, 1E-11, 1E-10), 0.5, 0.005)
model.assign_material("aniso_material", 'domain', "rosette")

model.create_pressure_inlet("inner_inlet", 1E+05)
model.assign_inlet("inner_inlet", "inner_rim")

model.create_vent("outer_vent", 0.0)
model.assign_vent("outer_vent", "outer_rim")

model.initialise_solver()
model.solve()

model.save_results()