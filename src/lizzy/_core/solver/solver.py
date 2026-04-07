#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.sensors import SensorManager
    from lizzy._core.gates import GatesManager
    from lizzy._core.cvmesh import Mesh
    from lizzy._core.materials import MaterialManager
    from lizzy._core.datatypes.simparams import SimulationParameters


import logging
import time
import numpy as np
from tqdm import tqdm
from lizzy._core.solver import *

logger = logging.getLogger("lizzy.solver")

from .timestep_manager import TimeStepManager
from .vsolvers import VelocitySolver
from .fillsolver import FillSolver
from .psolvers import PressureSolver, SolverType
from .preprocessor import Preprocessor
from .solverbcs import SolverBCs
from lizzy._core.datatypes.solverstate import SolverState



class Solver:
    def __init__(self, mesh:Mesh, gates_manager, simulation_parameters, material_manager:MaterialManager, sensor_manager:SensorManager, 
                 solver_type=SolverType.ITERATIVE_PETSC, solver_tol=1e-8, solver_max_iter=1000, 
                 solver_verbose=False, **solver_kwargs):
        
        # create / assign all core components
        self.mesh : Mesh = mesh
        self.material_manager = material_manager
        self.simulation_parameters : SimulationParameters = simulation_parameters
        self.fill_solver = FillSolver()
        self.vsolver = VelocitySolver(self.mesh.triangles)
        self.gates_manager : GatesManager = gates_manager 
        self.time_step_manager = TimeStepManager(mesh.mesh_view.n_nodes, mesh.mesh_view.n_triangles)
        self.preproc = Preprocessor(mesh, self.fill_solver, self.vsolver, material_manager, gates_manager, simulation_parameters)

        self._sensor_manager = sensor_manager
        self.bcs = SolverBCs()
        self.solver_type = solver_type
        if solver_type == SolverType.ITERATIVE_PETSC:
            try:
                import petsc4py
                petsc4py.init()
                from petsc4py import PETSc
            except ImportError:
                logger.warning(" PETSc not available. Reverting to DIRECT_SPARSE builtin solver.")
                self.solver_type = SolverType.DIRECT_SPARSE
        self.solver_tol = solver_tol
        self.solver_max_iter = solver_max_iter
        self.solver_verbose = solver_verbose
        self.solver_kwargs = solver_kwargs
        self.N_nodes = mesh.mesh_view.n_nodes
        self.K_sing = None
        self.f_orig = None
        self.state : SolverState = SolverState(self.mesh)
        

        self.perform_precalcs()
        self.initialise_new_solution()
    

    def perform_precalcs(self):
        self.K_sing, self.f_orig = self.preproc.run_preproc_sequence() # TODO: reorder nodes here to reduce bandwidth - then reorder the whole mesh and objects
        self.initialise_sensor_manager() # could move into preprocessor as this runs only once
    
    def initialise_sensor_manager(self):
        # assign sensors
        self._sensor_manager.initialise(self.mesh)



    def get_empty_nodes_idx(self, fill_factor):
        """
        Complementary to "update_bcs()", this updates the indices of all nodes with a fill factor < 1.0. These will be uses to assign an internal condition p=0.
        """
        return np.where(fill_factor < 1.0)[0]

    def fill_initial_cvs(self, state:SolverState):
        """
        Must be called AFTER calling "update_bcs()"
        """
        state.fill_factor_array[self.bcs.dirichlet_idx] = 1
        state.fill_factor_array[self.bcs.neumann_idx] = 1


    
    def generate_initial_time_step(self):
        time_0 = 0
        dt_0 = 0
        time_step_number = 0
        p_0 = np.full(len(self.mesh.nodes), self.bcs.p0_val, dtype=np.float64)
        fill_factor_0 = np.zeros(len(self.mesh.nodes))
        flow_front_0 = np.zeros(len(self.mesh.nodes))
        for idx, val in zip(self.bcs.dirichlet_idx, self.bcs.dirichlet_vals):
            p_0[idx] = val
            fill_factor_0[idx] = 1
            flow_front_0[idx] = 1
        v_0 = np.zeros((len(self.mesh.triangles), 3))
        v_nodal_0 = np.zeros((len(self.mesh.nodes), 3))
        initial_time_step = (time_step_number, time_0, dt_0, p_0, v_0, v_nodal_0, fill_factor_0, flow_front_0)
        return initial_time_step
        

    def initialise_new_solution(self):
        """
        Initialises a new solution, resetting all simulation variables. It is sufficient to call this method to reset the simulation and run again.
        """
        self.state.reset()
        self.state.next_wo_time = self.simulation_parameters.output_interval # TODO: this one and the next (current mu) are initialised manually... not pretty
        self.state.current_mu = self.material_manager.assigned_resin.mu
        self.bcs = SolverBCs()
        self.mesh.empty_cvs()
        self.gates_manager.reset_inlets()
        self.bcs.update(self.mesh, self.material_manager, self.gates_manager)
        self.fill_initial_cvs(self.state)
        p0_idxs = self.get_empty_nodes_idx(self.state.fill_factor_array)
        self.state.n_empty_cvs = len(p0_idxs)
        self.bcs.p0_idx = p0_idxs
        self.fill_solver.update_active_cvs_and_free_surface(self.state)
        self.time_step_manager.reset()
        initial_time_step = self.generate_initial_time_step()
        self.time_step_manager.save_timestep(*initial_time_step)
        self._sensor_manager.reset_sensors()
        # TODO: this first probe is temporary and should be cleaner
        self._sensor_manager.probe_current_solution(self.time_step_manager.p_buffer[0], self.time_step_manager.v_nodal_buffer[0], self.time_step_manager.fill_factor_buffer[0], 0.0)
        self.state.increment_time_step_counter()

    def handle_wo_criterion(self, dt):
        write_out = False
        next_time = self.state.current_time + dt

        if next_time >= self.state.step_end_time:
            dt = self.state.step_end_time - self.state.current_time
            write_out = True
            self.state.step_completed = True
            # Advance next_wo_time past step_end_time to avoid the duplicated Solution time bug that results in missing time step in Paraview. #TODO: this stuff is terrible: urge refactor of the whole write-out management. Works for now.
            if self.simulation_parameters.output_interval > 0.0:
                while self.state.next_wo_time <= self.state.step_end_time:
                    self.state.next_wo_time += self.simulation_parameters.output_interval
            return dt, write_out
        
        if self.simulation_parameters.output_interval > 0.0:
            if next_time >= self.state.next_wo_time:
                dt = self.state.next_wo_time - self.state.current_time
                self.state.next_wo_time += self.simulation_parameters.output_interval
                write_out = True
        else:
            write_out = True
            
        return dt, write_out

    def handle_wo_by_sensor_triggered(self, current_write_out, fill_factor_array):
        write_out = current_write_out
        triggered = self._sensor_manager.check_for_new_sensor_triggered(fill_factor_array, self.state.current_time)
        if triggered:
            write_out = True
            self.state.step_completed = True
        return write_out

    def solve_time_step(self):
        fill_factor = self.state.fill_factor_array
        free_surface = self.state.free_surface_array

        neumann_idxs = self.bcs.neumann_idx
        neumann_vals = self.bcs.neumann_vals
        f_neumann = self.f_orig.copy()
        for i in range(len(neumann_idxs)):
            f_neumann[neumann_idxs[i]] += neumann_vals[i]
        self.state.p_array = PressureSolver.solve_with_mask(
            self.K_sing, f_neumann, self.bcs, 
            self.solver_type, tol=self.solver_tol,
            max_iter=self.solver_max_iter, verbose=self.solver_verbose,
            **self.solver_kwargs)

        self.vsolver.update_elem_velocities(self.state)
        v_nodal_array = np.zeros((self.N_nodes, 3))

        self.fill_solver.update_active_cvs_and_free_surface(self.state)
        dt_candidate = self.fill_solver.calculate_time_step(self.state)
        dt, write_out = self.handle_wo_criterion(dt_candidate)

        self.fill_solver.fill_current_time_step(self.state, dt, self.simulation_parameters.fill_tolerance)

        # Update the filling time
        self.state.current_time += dt

        if self.simulation_parameters.end_step_when_sensor_triggered:
            write_out = self.handle_wo_by_sensor_triggered(write_out, fill_factor)
        # update the empty nodes idxs and count for next step
        p0_idxs = self.get_empty_nodes_idx(fill_factor)
        self.state.n_empty_cvs = len(p0_idxs)
        self.bcs.p0_idx = p0_idxs
        # always save and probe the final timestep
        if self.state.n_empty_cvs == 0:
            write_out = True
        if write_out:
            if not self.simulation_parameters.lightweight:
                self.time_step_manager.save_timestep(self.state.time_step_counter, self.state.current_time, dt, self.state.p_array, self.state.v_array, v_nodal_array, fill_factor, free_surface)
            self._sensor_manager.probe_current_solution(self.state.p_array, v_nodal_array, fill_factor, self.state.current_time)
        self.state.increment_time_step_counter()

    def solve(self):
        solution = None
        self.state.step_end_time = np.inf  # reset step end time for full solve
        self.bcs.update(self.mesh, self.material_manager, self.gates_manager) # TODO this is a bit hacky: need to update bcs before the first time step to correctly fill initial CVs and assign p0_idx. Should be more explicit or a cleaner way...
        total_cvs = self.N_nodes
        filled_cvs = total_cvs - self.state.n_empty_cvs
        logger.info(f" Solving started on {len(self.mesh.triangles)} elements and {self.N_nodes} nodes")
        pbar = tqdm(total=total_cvs, initial=filled_cvs,
                    desc="Fill progress",
                    bar_format="{l_bar}{bar}| t={postfix[0]:.2f}s [{elapsed}<{remaining}]",
                    postfix=[self.state.current_time],
                    ncols=80, disable=not self.simulation_parameters.progress_bar)
        solve_start = time.perf_counter()
        while self.state.n_empty_cvs > 0:
            self.solve_time_step()
            new_filled = total_cvs - self.state.n_empty_cvs
            pbar.update(new_filled - pbar.n)
            if self.simulation_parameters.progress_bar:
                pbar.postfix[0] = self.state.current_time
        solve_time = time.perf_counter() - solve_start
        pbar.close()
        logger.info(f" Solve completed in {solve_time:.2f} seconds")
        logger.info(f" Empty CVs: {self.state.n_empty_cvs}, fill time: {self.state.current_time:.2f} seconds")
        if not self.simulation_parameters.lightweight:
            solution = self.time_step_manager.pack_solution()
        return solution

    def solve_time_interval(self, time_interval:float):
        solution = None
        self.state.step_completed = False
        self.state.step_end_time = self.state.current_time + time_interval
        total_cvs = self.N_nodes
        filled_cvs = total_cvs - self.state.n_empty_cvs
        pbar = tqdm(total=total_cvs, initial=filled_cvs,
                    desc="Fill progress",
                    bar_format="{l_bar}{bar}| t={postfix[0]:.2f}s [{elapsed}<{remaining}]",
                    postfix=[self.state.current_time],
                    ncols=80, disable=not self.simulation_parameters.progress_bar)
        while self.state.step_completed == False and self.state.n_empty_cvs > 0:
            self.bcs.update(self.mesh, self.material_manager, self.gates_manager)
            if len(self.bcs.dirichlet_idx) == 0 and len(self.bcs.neumann_idx) == 0:
                self.solve_closed_inlets_time_step()
            else:
                self.solve_time_step()
            new_filled = total_cvs - self.state.n_empty_cvs
            pbar.update(new_filled - pbar.n)
            if self.simulation_parameters.progress_bar:
                pbar.postfix[0] = self.state.current_time
        pbar.close()
        if not self.simulation_parameters.lightweight:
            solution = self.time_step_manager.pack_solution()
        return solution
    
    def solve_closed_inlets_time_step(self):
        dt = self.simulation_parameters.output_interval
        dt, write_out = self.handle_wo_criterion(dt)
        if dt == 0.0:
            # skip this false time interval. TODO: There must be a better way to do this, but it works for now.
            return
        # Update the filling time
        self.state.current_time += dt
        # manually create (known) closed inlets solution
        fill_factor = self.state.fill_factor_array
        free_surface = self.state.free_surface_array
        p = np.zeros(self.N_nodes)
        self.state.v_array = np.zeros((len(self.mesh.triangles), 3))
        v_nodal_array = np.zeros((self.N_nodes, 3))
        if write_out:
            if not self.simulation_parameters.lightweight:
                self.time_step_manager.save_timestep(self.state.time_step_counter, self.state.current_time, dt, p, self.state.v_array, v_nodal_array, fill_factor, free_surface)
            self._sensor_manager.probe_current_solution(p, v_nodal_array, fill_factor, self.state.current_time)
        self.state.increment_time_step_counter()
