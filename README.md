[![Tests](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml/badge.svg)](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml)

# Lizzy
Welcome to Lizzy, a Liquid Composite Molding (LCM) simulation package written in Python.

<div style="display: flex; justify-content: left;">
<img src="docs/images/lizzy_logo_alpha_80.gif" alt="Lizzy logo" width="400">
</div>

Lizzy uses the FE/CV method to solve a macro-scale infusion problem in porous media. The solver is mainly designed to simulate composite resin infusion processes, but it can be generalised to other porous media like soils.
The solver name "Lizzy" is inspired by the character of Elizabeth Bennet, companion of Mr Darcy in Jane Austen's novel _Pride and Prejudice_.

### Development stage and Issues
This project is still in early development stage and has **not reached a release version** yet.
While the solver results are generally correct, there may still be cases where it fails.

It is recommended to wait for a first release before using Lizzy for your research. On the other hand, use of Lizzy for testing is welcome. If you do use Lizzy and encounter some issue, you can help improve the software faster by reporting what you encountered in the Issues sections.

## Installation
Lizzy is provided as a package.
It is advised to create a dedicated Python environment and use `pip` to install Lizzy in it.
Since Lizzy is still in early development and receives frequent updates, package versioning **is not adopted yet**.
Therefore, it is recommended to install the package in [editable mode](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode) by navigating inside the cloned `Lizzy` folder and running the command: `pip install -e .`. By doing so, a simple `git pull` inside the cloned repository will update the package to the latest commit. This is the recommended solution to keep Lizzy up to date until a version number will be released.

## Visualisation
The recommended software to visualise results from Lizzy is Paraview:
https://www.paraview.org

## Tutorials:
Some tutorial cases are provided below. The mesh files used in these examples are provided inside the folder [`/examples/meshes`](./examples/meshes). 

- [Channel flow experiment](docs/tutorials/rect.md)
- [Radial flow experiment](docs/tutorials/radial_aniso.md)
- [Material zones assignment](docs/tutorials/triforce.md)
- [Multi-inlet example](docs/tutorials/multi_inlet.md)

## Validation
Validation of the solver can be found [here](docs/validation.md). This section will expand as more features are added.

# UNDER CONSTRUCTION