<!--
Copyright 2025-2026 Simone Bancora, Paris Mulye

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
-->

[![Tests](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml/badge.svg)](https://github.com/simonebancora/Lizzy/actions/workflows/tests.yaml)
[![DOI](https://zenodo.org/badge/954238467.svg)](https://doi.org/10.5281/zenodo.15110049)

# Lizzy
Introducing Lizzy, a Liquid Composite Molding (LCM) simulation package written in Python.

<div style="display: flex; justify-content: left;">
<img src="https://raw.githubusercontent.com/simonebancora/Lizzy/main/docs/images/lizzy_logo_alpha_80.gif" alt="Lizzy logo" width="400">
</div>

Lizzy uses the FE/CV method to simulate a macro-scale infusion problem in porous media. The solver is mainly designed to simulate composite resin infusion processes, but can be generalised to any porous media.
The name "Lizzy" was inspired by the character of Elizabeth Bennet, companion of Mr Darcy in Jane Austen's novel _Pride and Prejudice_.

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.

> **Note:** Lizzy is still in early release stage. While we strive to maintain backwards API compatibility from now on, functionalities are still being added and API may still be subject to change. Contributions are not open yet.

### Installation

```bash
pip install lizzy-lib
```

#### Optional: PETSc solvers

Lizzy can use the PETSc library to achieve faster calculation times. To install:

```bash
pip install petsc petsc4py
```

### Documentation

The full [Documentation](https://lizzy.readthedocs.io/en/latest/) is available, though some parts may still be under construction.

### Visualisation
The recommended software to visualise results from Lizzy is [Paraview](https://www.paraview.org).



