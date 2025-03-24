# Radial flow experiment
In this example we simulate the radial infusion of an anisotropic material. The mesh file used in this example is [`Radial.msh`](../../examples/meshes/Radial.msh).

## Copy the mesh file
Create a folder in a preferred location and copy the mesh file [`Radial.msh`](../../examples/meshes/Radial.msh) in the new directory.
The mesh contains 3 domain tags ("physical groups" in msh format): _inner_rim_, _outer_rim_, _domain_.

## Create the script file
In the first line of the script, let's import Lizzy by:
```
import lizzy as liz
```
### Import the mesh file
Let's initialise a `Reader` object and read the mesh:
```
mesh_reader = liz.Reader("Radial.msh")
```
### Defining material properties
As usual, we must assign some process parameters to the `ProcessParameters`:
```
liz.ProcessParameters.assign(mu=0.1, wo_delta_time=100)
```
Next, we will define the properties of the material. Only one material domains is present in the mesh (_domain_), however we want to create an anisotropic material. We will assign different principal permeabiliy values:
```
rosette = liz.Rosette((1,0,0))
material = liz.PorousMaterial(1E-10, 1E-11, 1E-10, 0.5, 1.0)
liz.MaterialManager.add_material('domain', material, rosette)
```
In this case, we have assigned one order of magnitude of difference between $k_1$ and $k_2$. This will create a strongly anisotropic behaviour.

### Creating the simulation objects
Instantiate a `Mesh` object and a `BCManager` object:
```
mesh = liz.Mesh(mesh_reader)
bc_manager = liz.BCManager()
```

Create some boundary conditions. In this case, we will assign a constant inlet pressure $P_{in}=10^5$ [Pa] on the _inner_rim_ boundary:
```
inlet_1 = liz.Inlet('inner_rim', 1E+05)
bc_manager.add_inlet(inlet_1)
```

### Solve
The next step is to create an appropriate solver and call `solve` to run the filling simulation:
```
solver = liz.Solver(mesh, bc_manager)
solution = solver.solve(log="on")
```
### Write results
Create a `Writer` object to write out results:
```
writer = liz.Writer(mesh)
writer.save_results(solution, "Radial")
```

## The full script

```
import lizzy as liz

# read the mesh
mesh_reader = liz.Reader("../meshes/Radial.msh")

# assign some process parameters
liz.ProcessParameters.assign(mu=0.1, wo_delta_time=500)

# add a material to each material tag present in the mesh
rosette_1 = liz.Rosette((1,0,0))
material_1 = liz.PorousMaterial(1E-10, 1E-10, 1E-10, 0.5, 1.0)
liz.MaterialManager.add_material('domain', material_1, rosette_1)

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
writer.save_results(solution, "Radial")
```

# Solution visualisation
Load up the file `Radial_RES.xdmf` into Paraview to visualise the results:

<div style="display: flex; justify-content: center;">
<img src="./images/Radial_fill.png" alt="Radial fill solution" width="720">
</div>

We can see the typical elliptical flow front pattern that arises from the classical radial infusions.