#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
import numpy as np

@dataclass()
class TimeStep:
        index : int
        time : float
        dt : float
        P : any
        V : any
        fill_factor : any
        flow_front : any
        write_out : bool

class TimeStepManager:
    time_steps = []
    time_step_count = 0

    @classmethod
    def save_timestep(cls, time, dt, P, v_array, fill_factor, flow_front, write_out):

        
        if(v_array.shape[1]==3):
            v_full = v_array
        else:
            v3_nul = np.zeros((np.size(v_array,0), 1))
            v_full = np.hstack((v_array, v3_nul))
        timestep = TimeStep(cls.time_step_count, time, dt, P, v_full, np.clip(fill_factor, 0, 1), flow_front, write_out)
        cls.time_steps.append(timestep)
        cls.time_step_count += 1

    @classmethod
    def get_write_out_steps(cls):
        return [step for step in cls.time_steps if step.write_out == True]

    @classmethod
    def save_initial_timestep(cls, mesh, bcs):
        time_0 = 0
        p_0 = [0] * mesh.nodes.N
        fill_factor_0 = [0] * mesh.nodes.N
        flow_front_0 = [0] * mesh.nodes.N
        for i, val in enumerate(bcs.dirichlet_idx):
            p_0[val] = bcs.dirichlet_vals[i]
            fill_factor_0[val] = 1
            flow_front_0[val] = 1
        v_0 = np.zeros((mesh.triangles.N, 2))
        cls.save_timestep(time_0, 0, p_0, v_0, fill_factor_0, flow_front_0, True)

    @classmethod
    def pack_solution(cls):
        # flag the last time step as write-out:
        cls.time_steps[-1].write_out = True
        # populate solution with write-out time steps:
        wo_time_steps = cls.get_write_out_steps()
        solution = {"time_steps" : len(wo_time_steps),
                    "p" : [step.P for step in wo_time_steps],
                    "v" : [step.V.tolist() for step in wo_time_steps],
                    "time" : [step.time for step in wo_time_steps],
                    "fill_factor" : [step.fill_factor for step in wo_time_steps],
                    "free_surface" : [step.flow_front for step in wo_time_steps],
                    }
        return solution

    @classmethod
    def reset(cls):
        cls.time_steps = []
        cls.time_step_count = 0