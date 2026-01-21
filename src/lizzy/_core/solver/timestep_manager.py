#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.


import numpy as np
from lizzy._core.datatypes import TimeStep, Solution


class TimeStepManager:
    def __init__(self):
        self.time_steps = []
        self.time_step_count = 0

    def save_timestep(self, time, dt, P, v_array, v_nodal_array, fill_factor, flow_front, write_out):
        if(v_array.shape[1]==3):
            v_full = v_array
            v_nodal_full = v_nodal_array
        else:
            v3_nul = np.zeros((np.size(v_array,0), 1))
            v3_nodal_nul = np.zeros((np.size(v_nodal_array,0), 1))
            v_full = np.hstack((v_array, v3_nul))
            v_nodal_full = np.hstack((v_nodal_array, v3_nodal_nul))
        timestep = TimeStep(self.time_step_count, time, dt, P, v_full, v_nodal_full, np.clip(fill_factor, 0, 1), flow_front, write_out)
        self.time_steps.append(timestep)
        self.time_step_count += 1

    def get_write_out_steps(self):
        return [step for step in self.time_steps if step.write_out == True]

    def save_initial_timestep(self, mesh, bcs):
        time_0 = 0
        p_0 = [0] * mesh.nodes.N
        fill_factor_0 = [0] * mesh.nodes.N
        flow_front_0 = [0] * mesh.nodes.N
        for i, val in enumerate(bcs.dirichlet_idx):
            p_0[val] = bcs.dirichlet_vals[i]
            fill_factor_0[val] = 1
            flow_front_0[val] = 1
        v_0 = np.zeros((mesh.triangles.N, 2))
        v_nodal_0 = np.zeros((mesh.nodes.N, 2))
        self.save_timestep(time_0, 0, p_0, v_0, v_nodal_0, fill_factor_0, flow_front_0, True)

    def pack_solution(self):
        # flag the last time step as write-out regardless of its setting:
        self.time_steps[-1].write_out = True
        # populate solution with write-out time steps:
        wo_time_steps = self.get_write_out_steps()
        solution_obj = Solution(len(wo_time_steps),
                                    np.array([step.P for step in wo_time_steps]),
                                    np.array([step.V.tolist() for step in wo_time_steps]),
                                    np.array([step.V_nodal for step in wo_time_steps]),
                                    np.array([step.time for step in wo_time_steps]),
                                    np.array([step.fill_factor for step in wo_time_steps]),
                                    np.array([step.flow_front for step in wo_time_steps]),
                                    )
        solution = {"time_steps" : len(wo_time_steps),
                    "p" : [step.P for step in wo_time_steps],
                    "v" : [step.V.tolist() for step in wo_time_steps],
                    "v_nodal" : [step.V_nodal for step in wo_time_steps],
                    "time" : [step.time for step in wo_time_steps],
                    "fill_factor" : [step.fill_factor for step in wo_time_steps],
                    "free_surface" : [step.flow_front for step in wo_time_steps],
                    }
        return solution

    def reset(self):
        self.time_steps = []
        self.time_step_count = 0