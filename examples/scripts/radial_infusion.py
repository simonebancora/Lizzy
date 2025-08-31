import lizzy as liz

model = liz.LizzyModel()
model.read_mesh_file("../meshes/Radial.msh")
model.assign_simulation_parameters(mu=0.1, wo_delta_time=100)

rosette = liz.Rosette((1,1,0))
model.create_material(1E-10, 1E-11, 1E-10, 0.5, 1.0, "aniso_material")
model.assign_material("aniso_material", 'domain', rosette)

model.create_inlet(1E+05, "inner_inlet")
model.assign_inlet("inner_inlet", "inner_rim")

model.initialise_solver(solver_type=liz.SolverType.DIRECT_DENSE)
solution = model.solve()

model.save_results(solution, "Aniso")