import lizzy as liz

# read the mesh and instantiate
mesh_reader = liz.Reader("../meshes/Complex_rotated.msh")
mesh = liz.Mesh(mesh_reader)

# assign some process parameters
liz.ProcessParameters.assign(mu=0.1, wo_delta_time=100)

# add a material to each material tag present in the mesh
material_iso = liz.PorousMaterial(1E-10, 1E-10, 1E-10, 0.5, 1.0)
material_aniso = liz.PorousMaterial(1E-10, 1E-11, 1E-11, 0.5, 1.0)
material_racetrack = liz.PorousMaterial(1E-7, 1E-7, 1E-7, 0.5, 0.5)
rosette_ramp = liz.Rosette(mesh.nodes[12].coords, mesh.nodes[13].coords)
liz.MaterialManager.add_material('Lshape', material_iso)
liz.MaterialManager.add_material('ramp', material_aniso, rosette_ramp)
liz.MaterialManager.add_material('racetrack', material_racetrack)

# Create a BCManager and assign BCs
bc_manager = liz.BCManager()
inlet_1 = liz.Inlet('inlet', 1E+05)
bc_manager.add_inlet(inlet_1)

# Instantiate a solver and solve
solver = liz.Solver(mesh, bc_manager, liz.SolverType.DIRECT_SPARSE)
solution = solver.solve(log="on")

# Create a write-out object and save results
writer = liz.Writer(mesh)
writer.save_results(solution, "Complex_rotated")