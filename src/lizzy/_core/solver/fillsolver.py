#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np


class FillSolver:
    def __init__(self):
        self.all_fluxes_per_second = None
        self.map_cv_id_to_support_triangle_ids = {}
        self.map_cv_id_to_flux_terms = {}

    def find_free_surface_cvs(self, fill_factor_array : np.ndarray, cv_support_cvs_array : np.ndarray):
        """
        Finds the control volumes that are on the flow front. These cvs have a fill factor < 1.
        """
        candidate_mask = fill_factor_array < 1
        candidate_indices = np.nonzero(candidate_mask)[0]
        free_surface_array = np.zeros_like(fill_factor_array, dtype=int)
        neighbor_filled = np.array([np.any(fill_factor_array[cv_support_cvs_array[i]] >= 1) for i in candidate_indices])
        active_cv_ids = candidate_indices[neighbor_filled]
        free_surface_array[active_cv_ids] = 1
        return active_cv_ids, free_surface_array

    def calculate_time_step(self, active_cv_ids, fill_factor_array, cv_volumes_array, v_array):
        # calculate fluxes/s per each CV
        self.all_fluxes_per_second = [self.CalculateVolFluxes(v_array, cv_id) for cv_id in active_cv_ids]

        # calculate time step to fill one:
        candidate_dts = []
        for i in range(len(active_cv_ids)):
            active_cv_id = active_cv_ids[i]
            if self.all_fluxes_per_second[i] > 0:
                dt = ((1.00 - fill_factor_array[active_cv_id]) * cv_volumes_array[active_cv_id]) / self.all_fluxes_per_second[i]
                candidate_dts.append(dt)
        np.array(candidate_dts)
        dt = np.min(candidate_dts)
        return dt

    def fill_current_time_step(self, active_cv_ids, fill_factor_array, cv_volumes_array, dt, fill_tolerance):
        for i, id in enumerate(active_cv_ids):
            fill_factor_array[id] = min(fill_factor_array[id] + self.all_fluxes_per_second[i] * dt / cv_volumes_array[id], 1)
        for i in range(len(fill_factor_array)):
            if fill_factor_array[i] >= (1 - fill_tolerance):
                fill_factor_array[i] = 1
        return fill_factor_array

    def CalculateVolFluxes(self, v_array, cv_id):
        ids = self.map_cv_id_to_support_triangle_ids[cv_id] # retrieve from dictionary
        flux_terms_local = self.map_cv_id_to_flux_terms[cv_id] # retrieve from dictionary
        v_array_local = v_array[ids]
        cv_flux_per_s = np.sum(np.einsum('ij,ij->i', v_array_local, flux_terms_local))
        return cv_flux_per_s















# def find_free_surface_cvs_OLD(self, fill_factor_array, cv_support_cvs_array):
#     """
#     Finds the control volumes that are on the flow front. These cvs have a fill factor < 1.
#     """
#     free_surface_array = np.zeros_like(fill_factor_array)
#     active_cv_ids = []
#     for i, ff in enumerate(fill_factor_array):
#         if ff < 1:
#             neighbor_fills = fill_factor_array[cv_support_cvs_array[i]]
#             if np.max(neighbor_fills >= 1):
#                 active_cv_ids.append(i)
#                 free_surface_array[i] = 1
#
#     return active_cv_ids, free_surface_array


# def find_free_surface_cvs_SLOW(self, fill_factor_array, cv_adj_matrix):
#     """
#     Finds the control volumes that are on the flow front. These cvs have a fill factor < 1.
#     """
#     # cv_adj_matrix_full = cv_adj_matrix.toarray()
#     unfilled_cv_mask = np.diag((fill_factor_array < 1).astype(int))
#     filled_cv_mask = (fill_factor_array >= 1).astype(int)
#     free_surface_array = (unfilled_cv_mask @ cv_adj_matrix @ filled_cv_mask > 0).astype(int)
#     active_cv_ids = np.where(free_surface_array == 1)[0]
#     return active_cv_ids, free_surface_array