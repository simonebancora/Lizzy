[![Tests](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml/badge.svg)](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml)

# Lizzy
Welcome to Lizzy, a Liquid Composite Molding (LCM) simulation package written in Python.  
"Lizzy" is inspired by the character of Elizabeth Bennet, companion of Mr Darcy in Jane Austen's novel _Pride and Prejudice_.

### Development stage
Lizzy is currently in alpha development stage has not reached a release version yet.
This project is still in active development.

## Installation
Lizzy is provided as a package.
It is advised to create a python environment and use `pip` to install in the environment.
However, since Lizzy is still in early development and receives frequent updates, package versioning **is not adopted yet**.
Therefore, it is recommended to install the package in [editable mode](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode) by navigating inside the cloned `Lizzy` folder and running the command: `pip install -e .`. By doing so, a simple `git pull` inside the cloned repository will update the package to the latest commit.

## Visualisation
The recommended software to visualise results from Lizzy is Paraview:
https://www.paraview.org

## Tutorials:
Some tutorial cases are provided below. The scripts from the tutorials are available in [`/examples`](./examples).The mesh files used in these examples are provided inside the folder [`/examples/example_meshes`](./examples/example_meshes). 

- [Channel flow experiment](docs/tutorials/rect.md)
- [Radial flow experiment](docs/tutorials/radial_aniso.md)
- [Material zones assignment](docs/tutorials/triforce.md)
- [Multi-inlet example](docs/tutorials/multi_inlet.md)

## Validation
Validation of the solver can be found [here](docs/validation.md). This section will expand together with the improvement of Lizzy.

## The Lizzy way
The core focus of Lizzy is scriptability. The modukes