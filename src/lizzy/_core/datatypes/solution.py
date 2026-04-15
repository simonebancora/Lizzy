#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True, frozen=True)
class Solution:
    """A data class that stores the solution of a simulation.
    It stores a number of time steps (the ones that were flagged for write-out), up to the instant of its creation.
    
    Attributes
    ----------

    n_time_states : int
        The number of time states stored in the solution.
    time_step_idx : ndarray of int, shape (n_time_states,)
        The indices of the time steps that were stored as time states in the solution. The last index corresponds to the time step number at which this solution was saved.
    p : np.ndarray of float, shape (n_time_states, N_nodes)
        The pressure values at each step.
    v : np.ndarray of float, shape (n_time_states, N_elements, 3)
        The velocity values at each step.
    v_nodal : np.ndarray of float, shape (n_time_states, N_nodes, 3)
        The nodal velocity values at each step.
    time : np.ndarray of float, shape (n_time_states,)
        The simulation time values at each step.
    fill_factor : np.ndarray of float, shape (n_time_states, N_nodes)
        The fill factor values at each step.
    free_surface : np.ndarray of int, shape (n_time_states, N_nodes)
        The free surface values at each step.
    """
    n_time_states : int
    time_step_idx : np.ndarray
    p : np.ndarray
    v : np.ndarray
    v_nodal : np.ndarray
    time : np.ndarray
    fill_factor : np.ndarray
    free_surface : np.ndarray