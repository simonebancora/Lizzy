import lizzy

import logging                                                                                                          
logging.basicConfig(level=logging.INFO)

racetrack_gap = 0.002
racetrack_perm = racetrack_gap**2 / 12

model = lizzy.LizzyModel()
model.read_mesh_file("ChannelRacetrack.msh")
model.set_simulation_parameters(output_interval=5, progress_bar=True)

model.create_resin("resin_01", 0.1)
model.assign_resin("resin_01")

model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.005)
model.assign_material("domain_material", 'domain')

model.create_material("racetrack_material", (racetrack_perm, racetrack_perm, racetrack_perm), 1.0, 0.005)
model.assign_material("racetrack_material", 'racetrack')

model.create_pressure_inlet("inlet_left", 1E+05)
model.assign_inlet("inlet_left", "left_edge")

model.create_vent("vent_right", 0.0)
model.assign_vent("vent_right", "right_edge")

model.initialise_solver()
model.solve()

model.save_results()