#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import lizzy

class FillSolver:
    all_fluxes_per_second = None
    map_cv_id_to_support_triangle_ids = {}
    map_cv_id_to_flux_terms = {}

    @staticmethod
    def find_free_surface_cvs(fill_factor_array, cv_support_cvs_array):
        """
        Finds the control volumes that are on the flow front. These cvs have a fill factor < 1.
        """
        free_surface_array = np.zeros_like(fill_factor_array)
        active_cv_ids = []
        for i, ff in enumerate(fill_factor_array):
            if ff < 1:
                neighbor_fills = fill_factor_array[cv_support_cvs_array[i]]
                if np.any(neighbor_fills >= 1):
                    active_cv_ids.append(i)
                    free_surface_array[i] = 1
        return active_cv_ids, free_surface_array


    @classmethod
    def calculate_time_step(cls, active_cv_ids, fill_factor_array, cv_volumes_array, v_array):
        # calculate fluxes/s per each CV
        cls.all_fluxes_per_second = [cls.CalculateVolFluxes(v_array, cv_id) for cv_id in active_cv_ids]

        # calculate time step to fill one:
        candidate_dts = []
        for i in range(len(active_cv_ids)):
            active_cv_id = active_cv_ids[i]
            if cls.all_fluxes_per_second[i] > 0:
                dt = ((1.00 - fill_factor_array[active_cv_id]) * cv_volumes_array[active_cv_id]) / cls.all_fluxes_per_second[i]
                candidate_dts.append(dt)
        np.array(candidate_dts)
        dt = np.min(candidate_dts)
        return dt

    @classmethod
    def fill_current_time_step(cls, active_cv_ids, fill_factor_array, cv_volumes_array, dt, fill_tolerance):
        for i, id in enumerate(active_cv_ids):
            fill_factor_array[id] = min(fill_factor_array[id] + cls.all_fluxes_per_second[i] * dt / cv_volumes_array[id], 1)
        for i in range(len(fill_factor_array)):
            if fill_factor_array[i] >= (1 - fill_tolerance):
                fill_factor_array[i] = 1
        return fill_factor_array

    @classmethod
    def CalculateVolFluxes(cls, v_array, cv_id):
        ids = cls.map_cv_id_to_support_triangle_ids[cv_id] # retrieve from hash map
        flux_terms_local = cls.map_cv_id_to_flux_terms[cv_id] # retrieve from hash map
        v_array_local = v_array[ids]
        cv_flux_per_s = np.sum(np.einsum('ij,ij->i', v_array_local, flux_terms_local))
        return cv_flux_per_s