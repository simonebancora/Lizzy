#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING

from lizzy._core.cvmesh import mesh
if TYPE_CHECKING:
    from lizzy._core.sensors import SensorManager
    from lizzy._core.bcond import GatesManager
    from lizzy._core.cvmesh import Mesh
    from lizzy._core.materials import MaterialManager, Rosette, PorousMaterial
    from lizzy._core.datatypes import SimulationParameters

import sys
import numpy as np
import time
from lizzy._core.solver import *
from .timestep_manager import TimeStepManager
from .vsolvers import VelocitySolver
from .fillsolver import FillSolver
from .psolvers import PressureSolver, SolverType



class Preprocessor:
    def __init__(self, mesh:Mesh, fill_solver:FillSolver, vsolver:VelocitySolver, material_manager:MaterialManager, gates_manager:GatesManager, simulation_parameters:SimulationParameters):
        self.mesh = mesh
        self.fill_solver = fill_solver
        self.vsolver = vsolver
        self.material_manager = material_manager
        self.gates_manager = gates_manager
        self.simulation_parameters = simulation_parameters


    # 1. check things were assigned
    def assignment_checks(self):
        if not self.simulation_parameters.has_been_assigned:
            print(f"Warning: Simulation parameters were not assigned. Running with default values: wo_delta_time={self.simulation_parameters.wo_delta_time}")
        if self.material_manager._assigned_resin == None:
            print(f"ERROR: No resin assigned to the model. Create a resin using `LizzyModel.create_resin` and assign it using `LizzyModel.assign_resin`")
            sys.exit(1)
        if self.material_manager._resin_was_assigned == False:
            print("WARNING-MATERIAL MANAGER: No resin was assigned. Running simulation with default resin: viscosity value 0.1 Pa.s. Create a resin using `LizzyModel.create_resin` and assign it using `LizzyModel.assign_resin` to remove this warning.")
        self.gates_manager.assert_unique_boundary_assignments()

    # 2. assign materials to elements
    def assign_materials_to_elements(self):
        materials = self.material_manager.assigned_materials
        rosettes = self.material_manager.assigned_rosettes
        for tri in self.mesh.triangles:
            try:
                material : PorousMaterial = materials[tri.material_tag]
                if material.is_isotropic:
                    tri.k = material.k_princ
                else:
                    rosette : Rosette = rosettes[tri.material_tag]
                    u, v, w = rosette.project_along_normal(tri.n)
                    R = np.array([u, v, w]).T
                    tri.k = R @ material.k_princ @ R.T
                tri.porosity = materials[tri.material_tag].porosity
                tri.h = materials[tri.material_tag].thickness
            except KeyError:
                exit(f"Mesh contains unassigned material tag: {tri.material_tag}")

    # 3. setup control volumes
    def setup_cvs(self):
        cvs = self.mesh.CVs
        n_cvs = len(cvs)
        node_idx_to_flux_ndarray: list[np.ndarray] = [None]*n_cvs
        for i in range(n_cvs):
            cvs[i].calculate_area_and_volume()
            node_idx_to_flux_ndarray[i] = cvs[i].compute_flux_terms()
        self.mesh.mesh_view.node_idx_to_flux_ndarray = node_idx_to_flux_ndarray

    # 4. assign data to fill solver
    def assign_fill_solver_maps(self):
        self.fill_solver.map_cv_id_to_support_triangle_ids = self.mesh.mesh_view.node_idx_to_tri_idxs
        self.fill_solver.map_cv_id_to_flux_terms = self.mesh.mesh_view.node_idx_to_flux_ndarray
    
    # 5. assemble global stiffness matrix (singular)
    def assemble_global_stiffnes_matrix(self):
        mu = self.material_manager.assigned_resin.mu
        K_sing, f_orig = fe.Assembly(self.mesh, mu, sparse=True)
        return K_sing, f_orig

    def run_preproc_sequence(self):
        print("Preprocessing...")
        self.assignment_checks()
        self.assign_materials_to_elements()
        self.setup_cvs()
        self.assign_fill_solver_maps()
        K_sing, f_orig = self.assemble_global_stiffnes_matrix()
        self.vsolver.precalculate_darcy_operator(self.mesh.triangles)
        return K_sing, f_orig
    
    





