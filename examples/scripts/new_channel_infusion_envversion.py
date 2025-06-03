import lizzy as liz

env = liz.LizzyEnv()

env.read_mesh_file("../meshes/Rect1M_R1.msh")

material = env.create_porous_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "pippo")
env.assign_material(material, 'domain')


inlet = liz.create_inlet(100000)
env.assign_inlet(inlet, "left_edge")

env.initialise_solver(liz.SolverType.DIRECT_DENSE)
solution = env.solve()