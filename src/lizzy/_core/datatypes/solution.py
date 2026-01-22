from dataclasses import dataclass
import numpy as np

@dataclass(slots=True, frozen=True)
class Solution:
    """A data class that stores the solution of a simulation.
    It stores a number of time steps (the ones that were flagged for write-out), up to the instant of its creation.
    
    Attributes
    ----------

    time_steps_in_solution : int
        The number of time steps stored in the solution.
    time_step_idx : ndarray of int, shape (time_steps_in_solution,)
        The indices of the time steps stored in the solution. The last index corresponds to the time step number at which this solution was saved.
    p : np.ndarray of float, shape (time_steps_in_solution, N_nodes)
        The pressure values at each step.
    v : np.ndarray of float, shape (time_steps_in_solution, N_elements, 3)
        The velocity values at each step.
    v_nodal : np.ndarray of float, shape (time_steps_in_solution, N_nodes, 3)
        The nodal velocity values at each step.
    time : np.ndarray of float, shape (time_steps_in_solution,)
        The simulation time values at each step.
    fill_factor : np.ndarray of float, shape (time_steps_in_solution, N_nodes)
        The fill factor values at each step.
    free_surface : np.ndarray of int, shape (time_steps_in_solution, N_nodes)
        The free surface values at each step.
    """
    time_steps_in_solution : int
    time_step_idx : np.ndarray
    p : np.ndarray
    v : np.ndarray
    v_nodal : np.ndarray
    time : np.ndarray
    fill_factor : np.ndarray
    free_surface : np.ndarray