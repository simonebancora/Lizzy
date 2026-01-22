from dataclasses import dataclass
import numpy as np

@dataclass(slots=True)
class Solution:
    time_steps_in_solution : int
    time_step_idx : np.ndarray
    p : np.ndarray
    v : np.ndarray
    v_nodal : np.ndarray
    time : np.ndarray
    fill_factor : np.ndarray
    free_surface : np.ndarray