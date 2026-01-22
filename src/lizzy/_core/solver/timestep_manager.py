#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.


import numpy as np
from lizzy._core.datatypes import TimeStep, Solution


class TimeStepManager:
    def __init__(self, n_nodes, n_elements):
        self.n_nodes : int = n_nodes
        self.n_elements : int = n_elements
        self.time_step_buffer_size : int = None
        self.time_step_count : int = None
        self.time_buffer : np.ndarray = None
        self.dt_buffer : np.ndarray = None
        self.p_buffer : np.ndarray = None
        self.v_buffer : np.ndarray = None
        self.v_nodal_buffer : np.ndarray = None
        self.fill_factor_buffer : np.ndarray = None
        self.flow_front_buffer : np.ndarray = None
        self.write_out_buffer : np.ndarray = None
        self.reset()

    def save_timestep(self, time, dt, P, v_array, v_nodal_array, fill_factor, flow_front, write_out):
        if self.time_step_count >= self.time_step_buffer_size:
            self.grow_buffers()
        self.time_buffer[self.time_step_count] = time
        self.dt_buffer[self.time_step_count] = dt
        self.p_buffer[self.time_step_count, :] = P
        self.v_buffer[self.time_step_count, :, :] = v_array
        self.v_nodal_buffer[self.time_step_count, :, :] = v_nodal_array
        self.fill_factor_buffer[self.time_step_count, :] = fill_factor
        self.flow_front_buffer[self.time_step_count, :] = flow_front
        self.write_out_buffer[self.time_step_count] = write_out
        self.time_step_count += 1

    
    def grow_buffers(self):
            new_size = self.time_step_buffer_size * 2
            self.time_buffer = np.resize(self.time_buffer, new_size)
            self.dt_buffer = np.resize(self.dt_buffer, new_size)
            self.p_buffer = np.resize(self.p_buffer, (new_size, self.p_buffer.shape[1]))
            self.v_buffer = np.resize(self.v_buffer, (new_size, self.v_buffer.shape[1], self.v_buffer.shape[2]))
            self.v_nodal_buffer = np.resize(self.v_nodal_buffer, (new_size, self.v_nodal_buffer.shape[1], self.v_nodal_buffer.shape[2]))
            self.fill_factor_buffer = np.resize(self.fill_factor_buffer, (new_size, self.fill_factor_buffer.shape[1]))
            self.flow_front_buffer = np.resize(self.flow_front_buffer, (new_size, self.flow_front_buffer.shape[1]))
            self.write_out_buffer = np.resize(self.write_out_buffer, new_size)
            self.time_step_buffer_size = new_size


    def get_write_out_indices(self):
        write_out_array = self.write_out_buffer[:self.time_step_count]
        return np.nonzero(write_out_array)[0]

    def pack_solution(self):
        # flag the last time step as write-out regardless of its setting:
        if self.time_step_count > 0:
            self.write_out_buffer[self.time_step_count - 1] = True
        # populate solution with write-out time steps:
        wo_idx = self.get_write_out_indices()
        solution_obj = Solution(len(wo_idx),
                                wo_idx,
                                self.p_buffer[wo_idx, :],
                                self.v_buffer[wo_idx, :, :],
                                self.v_nodal_buffer[wo_idx, :, :],
                                self.time_buffer[wo_idx],
                                self.fill_factor_buffer[wo_idx, :],
                                self.flow_front_buffer[wo_idx, :],
                                )
        # solution = {"time_steps" : len(wo_idx),
        #             "p" : [step.P for step in wo_time_steps],
        #             "v" : [step.V.tolist() for step in wo_time_steps],
        #             "v_nodal" : [step.V_nodal for step in wo_time_steps],
        #             "time" : [step.time for step in wo_time_steps],
        #             "fill_factor" : [step.fill_factor for step in wo_time_steps],
        #             "free_surface" : [step.flow_front for step in wo_time_steps],
        #             }
        return solution_obj

    def reset(self):
        self.time_step_buffer_size = 1000
        self.time_step_count = 0
        self.time_buffer = np.empty(self.time_step_buffer_size, dtype=float)
        self.dt_buffer = np.empty(self.time_step_buffer_size, dtype=float)
        self.p_buffer = np.empty((self.time_step_buffer_size, self.n_nodes), dtype=float)
        self.v_buffer = np.empty((self.time_step_buffer_size, self.n_elements, 3), dtype=float)
        self.v_nodal_buffer = np.empty((self.time_step_buffer_size, self.n_nodes, 3), dtype=float)
        self.fill_factor_buffer = np.empty((self.time_step_buffer_size, self.n_nodes), dtype=float)
        self.flow_front_buffer = np.empty((self.time_step_buffer_size, self.n_nodes), dtype=int)
        self.write_out_buffer = np.empty(self.time_step_buffer_size, dtype=bool)