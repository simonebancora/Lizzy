import lizzy as liz

# read the mesh
mesh_reader = liz.Reader("../meshes/Triforce_R1.msh")

# assign some process parameters
liz.ProcessParameters.assign(mu=0.1, wo_delta_time=100)

# add a material to each material tag present in the mesh
material_domain = liz.PorousMaterial(1E-10, 1E-10, 1E-10, 0.5, 1.0)
material_low_perm = liz.PorousMaterial(1E-13, 1E-13, 1E-13, 0.5, 1.0)
liz.MaterialManager.add_material('background', material_domain)
liz.MaterialManager.add_material('triforce', material_low_perm)

# Create a lizzy mesh object
mesh = liz.Mesh(mesh_reader)
bc_manager = liz.BCManager()

# Create an Inlet (or more) and add it to the inlets group
inlet_1 = liz.Inlet('inner_rim', 1E+05)
bc_manager.add_inlet(inlet_1)

# Instantiate a solver and solve
solver = liz.Solver(mesh, bc_manager, liz.SolverType.DIRECT_SPARSE)
solution = solver.solve(log="on")

# Create a write-out object and save results
writer = liz.Writer(mesh)
writer.save_results(solution, "Triforce_R1")