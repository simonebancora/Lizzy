<!--
Copyright 2025-2025 Simone Bancora, Paris Mulye

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
-->

[![Tests](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml/badge.svg)](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml)

# Lizzy
Introducing Lizzy, a Liquid Composite Molding (LCM) simulation package written in Python.

<div style="display: flex; justify-content: left;">
<img src="docs/images/lizzy_logo_alpha_80.gif" alt="Lizzy logo" width="400">
</div>

Lizzy uses the FE/CV method to simulate a macro-scale infusion problem in porous media. The solver is mainly designed to simulate composite resin infusion processes, but can be generalised to any porous media.
The name "Lizzy" was inspired by the character of Elizabeth Bennet, companion of Mr Darcy in Jane Austen's novel _Pride and Prejudice_.

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

### Development stage and Issues
This project is still in early development stage and has **not reached a release version** yet.
While the solver results are generally correct, there may still be cases where it fails.
If you use Lizzy and encounter some issue, you can help improve the software faster by reporting what you encountered in the [Issues](https://github.com/simonebancora/Lizzy/issues) section.

## Installation
Lizzy is provided as a package.
It is advised to create a dedicated Python environment and use the `pip` package manager to install Lizzy in it.
Since Lizzy is still in early development and receives frequent updates, package versioning **is not adopted yet**.
Therefore, it is recommended to install the package in [editable mode](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode).

## Visualisation
The recommended software to visualise results from Lizzy is Paraview:
https://www.paraview.org

## Tutorials:
Some tutorial cases are provided below. The mesh files used in these examples are provided inside the folder [`/examples/meshes`](./examples/meshes). 

- [Channel flow experiment](docs/github/tutorials/rect.md)
- [Radial flow experiment](docs/github/tutorials/radial_aniso.md)
- [Material zones assignment](docs/github/tutorials/triforce.md)


## Validation
Validation of the solver can be found [here](docs/github/validation.md). This section will expand as more features are added.

# DOCUMENTATION UNDER CONSTRUCTION