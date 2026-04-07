#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.cvmesh import Mesh

import numpy as np

class SolverState:
    __slots__ = (                                     
        'mesh', 'fill_factor_array', 'p_array', 'v_array', 'free_surface_array',                                                                                                                                                                   
        'cv_volumes_array', 'cv_idx_to_support_cv_idxs', 'active_cv_ids', 'current_mu',
        'current_time', 'time_step_counter', 'n_empty_cvs',                                                                                                                                                          
        'next_wo_time', 'step_end_time', 'step_completed',                                                                                                                                                           
    )
    def __init__(self, mesh:Mesh):
        self.mesh = mesh
        self.fill_factor_array: np.ndarray = None
        self.p_array: np.ndarray = None
        self.v_array: np.ndarray = None
        self.free_surface_array: np.ndarray = None
        self.cv_volumes_array = None
        self.cv_idx_to_support_cv_idxs = None
        self.active_cv_ids = None
        self.current_mu = None

        self.n_empty_cvs = np.inf

        self.current_time = 0.0
        self.time_step_counter = 0
        self.next_wo_time = np.inf
        self.step_end_time = np.inf
        self.step_completed = False
    
    def reset(self):
        self.fill_factor_array: np.ndarray = np.zeros(len(self.mesh.nodes), dtype=float)
        self.v_array: np.ndarray = np.zeros((len(self.mesh.triangles), 3), dtype=float)
        self.p_array: np.ndarray = np.zeros(len(self.mesh.nodes), dtype=float)
        self.free_surface_array: np.ndarray = np.empty(len(self.mesh.nodes))
        self.cv_volumes_array = np.array([cv.vol for cv in self.mesh.CVs])
        self.cv_idx_to_support_cv_idxs = self.mesh.mesh_view.node_idx_to_node_idxs
        self.active_cv_ids = None

        self.n_empty_cvs = np.inf

        self.current_time = 0.0
        self.time_step_counter = 0
        self.next_wo_time = np.inf
        self.step_end_time = np.inf
        self.step_completed = False
    
    def increment_time_step_counter(self):
        self.time_step_counter += 1
