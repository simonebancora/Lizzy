import lizzy

n_elems = [16, 64, 256, 1024, 4096]

print("Validation of the filling time for a channel flow experiment. Theoretical solution: 2500 seconds")

for ne in n_elems:
    model = lizzy.LizzyModel()
    model.read_mesh_file(f"./Rect_validation_{ne}.msh")
    model.set_simulation_parameters(output_interval=100, progress_bar=False, in_memory_solve=True)

    model.create_resin("resin_01", 0.1)
    model.assign_resin("resin_01")

    model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.5, 0.01)
    model.assign_material("domain_material", 'domain')

    model.create_pressure_inlet("inlet_left", 100000)
    model.assign_inlet("inlet_left", "left_edge")

    model.create_vent("vent_right", vacuum_pressure=0.0)
    model.assign_vent("vent_right", "right_edge")

    model.initialise_solver()

    model.solve()

    print(f"Number of elements: {ne}, filling time: {model.current_time:.1f} seconds, rel. error: {abs(model.current_time - 2500)/2500 *100:.2f}%")

    # model.save_results()