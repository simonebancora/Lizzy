# Lee, Y. M., et al. "Analysis of flow in the RTM Process." SAE transactions (1989): 65-75.
# Eq. (A-4) : 
# r_0 = 1, r_m = 2, phi = 0.6, eta = 0.1, K = 1e-10, P0 = 1e5
# Then the filling time = 3817.77 seconds

import lizzy

n_elems = [3600]

print("Validation of the filling time for a radial flow experiment. Theoretical solution: 3818 seconds")

for ne in n_elems:
    model = lizzy.LizzyModel()

    model.read_mesh_file(f"./quarter_annulus_{ne}.msh")
    model.set_simulation_parameters(output_interval=50, fill_tolerance=0.001, progress_bar=False, in_memory_solve=True)

    model.create_resin("resin", 0.1)
    model.assign_resin("resin")

    model.create_material("domain_material", (1E-10, 1E-10, 1E-10), 0.6, 1.0)
    model.assign_material("domain_material", 'domain')

    model.create_pressure_inlet("inner_radius", 1e+05)
    model.assign_inlet("inner_radius", "inlet")

    model.initialise_solver()
    model.solve()

    print(f"Number of elements: {ne}, filling time: {model.current_time:.2f} seconds, rel. error: {abs(model.current_time - 3818)/3818 *100:.3f}%")

    model.save_results()