#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.datatypes.solverdata import SolverState

import numpy as np

class FillSolver:
    def __init__(self):
        self.all_fluxes_per_second = None
        self.map_cv_id_to_support_triangle_ids = {}
        self.map_cv_id_to_flux_terms = {}

    def update_active_cvs_and_free_surface(self, state:SolverState):
        fill_factor_array : np.ndarray = state.fill_factor_array
        cv_idx_to_support_cv_idxs : list[np.ndarray] = state.cv_idx_to_support_cv_idxs

        """
        Finds the control volumes that are on the flow front. These cvs have a fill factor < 1.
        """
        candidate_mask = fill_factor_array < 1
        candidate_indices = np.nonzero(candidate_mask)[0]
        free_surface_array = np.zeros_like(fill_factor_array, dtype=int)
        neighbor_filled = np.array([np.any(fill_factor_array[cv_idx_to_support_cv_idxs[i]] >= 1) for i in candidate_indices])
        active_cv_ids = candidate_indices[neighbor_filled]
        free_surface_array[active_cv_ids] = 1
        state.active_cv_ids = active_cv_ids
        state.free_surface_array = free_surface_array

    def calculate_time_step(self, state:SolverState):
        active_cv_ids = state.active_cv_ids
        fill_factor_array = state.fill_factor_array
        cv_volumes_array = state.cv_volumes_array
        v_array = state.v_array
        # calculate fluxes/s per each CV
        self.all_fluxes_per_second = np.array([self.CalculateVolFluxes(v_array, cv_id) for cv_id in active_cv_ids])

        # calculate time step to fill one:
        positive = self.all_fluxes_per_second > 0
        dt = np.min(
            (1.0 - fill_factor_array[active_cv_ids[positive]]) * cv_volumes_array[active_cv_ids[positive]] / self.all_fluxes_per_second[positive]
        )
        return dt

    def fill_current_time_step(self, state:SolverState, dt, fill_tolerance):
        active_cv_ids = state.active_cv_ids
        fill_factor_array = state.fill_factor_array
        cv_volumes_array = state.cv_volumes_array
        fill_factor_array[active_cv_ids] = np.minimum(
            fill_factor_array[active_cv_ids] + self.all_fluxes_per_second * dt / cv_volumes_array[active_cv_ids],
            1.0
        )
        fill_factor_array[fill_factor_array >= (1 - fill_tolerance)] = 1.0

    def CalculateVolFluxes(self, v_array, cv_id):
        ids = self.map_cv_id_to_support_triangle_ids[cv_id] # retrieve from dictionary
        flux_terms_local = self.map_cv_id_to_flux_terms[cv_id] # retrieve from dictionary
        v_array_local = v_array[ids]
        cv_flux_per_s = np.sum(np.einsum('ij,ij->i', v_array_local, flux_terms_local))
        return cv_flux_per_s