# Material zones assignment
In this example we will use the Material Manager of Lizzy to assign different properties to regions in the domain. The mesh file used in this example is [`Triforce_R1.msh`](../../examples/example_meshes/Triforce_R1.msh).

## Copy the mesh file
Create a folder in a preferred location and copy the mesh file [`Triforce_R1.msh`](../../examples/example_meshes/Triforce_R1.msh) in the new directory.
The mesh contains 4 domain tags ("physical groups" in msh format): _inner_rim_, _outer_rim_, _background_, _triforce_.

## Setup
The case setup in Lizzy is identical to the example [Radial flow experiment](docs/tutorials/radial_aniso.md), therefore we won't repeat the steps here. The only difference lies in the assignment of material properties, therefore we will focus on that aspect only.

## Materials assignment
We now have 4 domain tags in the mesh, of which 2 are element tags (_background_, _triforce_). Therefore, we can use the Material Manager as ususal, simply adding a new material assignment expression:
```
liz.MaterialsMap.add_material('background', liz.PorousMaterial(1E-10, 1E-10, 0.0, 0.5, 1.0))
liz.MaterialsMap.add_material('triforce', liz.PorousMaterial(1E-13, 1E-13, 0.0, 0.5, 1.0))
```
In this case, we have assigned a different isotropic material to each element tag.

## The full script
```
import lizzy as liz

# read the mesh
mesh_reader = liz.Reader("Triforce_R1.msh")

# assign some process parameters
liz.ProcessParameters.assign(mu=0.1, wo_delta_time=100)

# add a material to each material tag present in the mesh
liz.MaterialManager.add_material('background', liz.PorousMaterial(1E-10, 1E-10, 0.0, 0.5, 1.0))
liz.MaterialManager.add_material('triforce', liz.PorousMaterial(1E-13, 1E-13, 0.0, 0.5, 1.0))

# Create a lizzy mesh object
mesh = liz.Mesh(mesh_reader)

# Create an Inlet (or more) and add it to the inlets group
inlet_1 = liz.Inlet('inner_rim', 1E+05)
bcs = liz.BCGroup(inlets=[inlet_1])

# Instantiate a solver and solve
solver = liz.Solver(mesh, bcs, liz.SolverType.DIRECT_SPARSE)
solution = solver.solve(log="on")

# Create a write-out object and save results
writer = liz.Writer(mesh)
writer.save_results(solution, "Triforce_R1")
```

# Solution visualisation
We load the file `results/Triforce_R1_RES.xdmf` into Paraview to visualise the results:

<div style="display: flex; justify-content: center;">
<img src="./images/trifoce_fill.png" alt="Alt text" width="720">
</div>

<div style="display: flex; justify-content: center;">
<img src="./images/triforce_pressure.png" alt="Alt text" width="720">
</div>

We can see the strong jump in the pressure field between the background and the low-permeability region, which doesn't get filled until the end of the infusion.