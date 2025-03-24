#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import lizzy

class FillSolver:
    all_fluxes_per_second = None
    @staticmethod
    def find_free_surface_cvs(CVs):
        """
        Finds the control volumes that are on the flow front. These cvs have a fill factor < 1.
        """
        active_cvs = []
        for cv in CVs:
            cv.free_surface = 0
            if cv.fill < 1 <= np.max([c.fill for c in cv.support_CVs]):
                cv.free_surface = 1
                active_cvs.append(cv)
        return active_cvs


    @classmethod
    def calculate_time_step(cls, active_cvs, v_array):
        # calculate fluxes/s per each CV
        cls.all_fluxes_per_second = []
        for cv in active_cvs:
            cv_fluxes_per_s = cv.CalculateVolFluxes(v_array)
            cls.all_fluxes_per_second.append(cv_fluxes_per_s)

        # calculate time step to fill one:
        candidate_dts = []
        for i, cv in enumerate(active_cvs):
            if cls.all_fluxes_per_second[i] > 0:
                dt = ((1.00-cv.fill)*cv.vol)/cls.all_fluxes_per_second[i]
                candidate_dts.append(dt)
        np.array(candidate_dts)
        dt = np.min(candidate_dts)
        return dt

    @classmethod
    def fill_current_time_step(cls, active_cvs, dt):
        for i, cv in enumerate(active_cvs):
            cv.fill = min(cv.fill + cls.all_fluxes_per_second[i]*dt / cv.vol, 1)
        for cv in active_cvs:
            if cv.fill >= (1-lizzy.ProcessParameters.fill_tolerance):
                cv.fill = 1