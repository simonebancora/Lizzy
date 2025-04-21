import lizzy as liz

mesh_reader = liz.Reader("../meshes/Radial.msh")
mesh = liz.Mesh(mesh_reader)

liz.ProcessParameters.assign(mu=0.1, wo_delta_time=500)

rosette = liz.Rosette((1,0,0))
material = liz.PorousMaterial(1E-10, 1E-11, 1E-10, 0.5, 1.0)
liz.MaterialManager.add_material('domain', material, rosette)

bc_manager = liz.BCManager()
inlet_1 = liz.Inlet('inner_rim', 1E+05)
bc_manager.add_inlet(inlet_1)

solver = liz.Solver(mesh, bc_manager, liz.SolverType.DIRECT_SPARSE)
solution = solver.solve(log="on")

writer = liz.Writer(mesh)
writer.save_results(solution, "Radial")