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


import numpy as np
import time
from lizzy._core.solver import *
from lizzy.exceptions import MeshError, ConfigurationError
from .timestep_manager import TimeStepManager
from .vsolvers import VelocitySolver
from .fillsolver import FillSolver
from .psolvers import PressureSolver, SolverType
from .preprocessor import Preprocessor
from lizzy._core.gates.gates import InletType


class SolverBCs:
    __slots__ = ("dirichlet_idx", "dirichlet_vals", "neumann_idx", "neumann_vals", "p0_idx", "p0_val")

    def __init__(self):
        self.dirichlet_idx = np.empty(0, dtype=np.uint32)
        self.dirichlet_vals = np.empty(0, dtype=np.float64)
        self.neumann_idx = np.empty(0, dtype=np.uint32)
        self.neumann_vals = np.empty(0, dtype=np.float64)
        self.p0_idx = np.empty(0, dtype=np.uint32)
        self.p0_val = 0.0

class Solver:
    def __init__(self, mesh:Mesh, gates_manager, simulation_parameters, material_manager:MaterialManager, sensor_manager:SensorManager, 
                 solver_type=SolverType.ITERATIVE_PETSC, solver_tol=1e-8, solver_max_iter=1000, 
                 solver_verbose=False, **solver_kwargs):
        
        # create / assign all core components
        self.mesh : Mesh = mesh
        self.fill_solver = FillSolver()
        self.material_manager = material_manager
        self.simulation_parameters = simulation_parameters
        self.vsolver = VelocitySolver(self.mesh.triangles)
        self.preproc = Preprocessor(mesh, self.fill_solver, self.vsolver, material_manager, gates_manager, simulation_parameters)

        self.gates_manager : GatesManager = gates_manager 
        self.time_step_manager = TimeStepManager(mesh.mesh_view.n_nodes, mesh.mesh_view.n_triangles)
        self._sensor_manager = sensor_manager
        self.bcs = SolverBCs()
        self.solver_type = solver_type
        if solver_type == SolverType.ITERATIVE_PETSC:
            try:
                import petsc4py
                petsc4py.init()
                from petsc4py import PETSc
            except ImportError:
                print("Import Error: PETSc not available. Reverting to DIRECT_SPARSE builtin solver.")
                self.solver_type = SolverType.DIRECT_SPARSE
        self.solver_tol = solver_tol
        self.solver_max_iter = solver_max_iter
        self.solver_verbose = solver_verbose
        self.solver_kwargs = solver_kwargs
        self.N_nodes = mesh.mesh_view.n_nodes
        self.K_sing = None
        self.f_orig = None
        self.current_time = 0
        self.time_step_counter = 0
        self.n_empty_cvs = np.inf
        self.next_wo_time = self.simulation_parameters.output_interval
        self.step_end_time = np.inf
        self.step_completed = False
        self.solver_vars = {"fill_factor_array" : np.zeros(self.N_nodes, dtype=float),
                            "free_surface_array" : np.empty(self.N_nodes),
                            "cv_volumes_array" : np.empty(self.N_nodes),}
        self.cv_support_cvs_array = self.mesh.mesh_view.node_idx_to_node_idxs # TODO do cleaner

        self.perform_precalcs()
        self.initialise_new_solution()
    

    def perform_precalcs(self):
        self.K_sing, self.f_orig = self.preproc.run_preproc_sequence() # TODO: reorder nodes here to reduce bandwidth - then reorder the whole mesh and objects
        self.vectorize_solver_vars()
        self.initialise_sensor_manager() # could move into preprocessor as this runs only once
    
    def initialise_sensor_manager(self):
        # assign sensors
        self._sensor_manager.initialise(self.mesh)

    def vectorize_solver_vars(self):
        # precalculate vectorised version of all variables
        # TODO this part can go faster
        cv_volumes_list = []
        for cv in self.mesh.CVs:
            cv_volumes_list.append(cv.vol)
        self.solver_vars["cv_volumes_array"] = np.array(cv_volumes_list, dtype=float)
        

    def update_bcs(self):
        # TODO this is more "update inlet dirichlet bcs" since it only applies pressure (doesn't add empty 0 pressure). It can be faster, but it doesn't run often (only at beginning of time intervals) so it's not critical
        dirichlet_idxs = []
        dirichlet_vals = []
        neumann_idxs_pairs = []
        neumann_vals_per_idx_pair = []
        dict_boundary_name_to_inlet_obj = self.gates_manager._assigned_inlets
        phys_boundary_names_set = self.mesh.mesh_view.phys_boundary_names_set
        viscosity = self.material_manager.assigned_resin.mu
        for boundary_name, inlet in dict_boundary_name_to_inlet_obj.items():
            if boundary_name not in phys_boundary_names_set:
                raise MeshError(f"Mesh does not contain physical tag: '{boundary_name}'.")
            match inlet.type:
                case InletType.PRESSURE:
                    node_idxs = self.mesh.mesh_view.phys_boundary_name_to_node_idxs[boundary_name]
                    if inlet.is_open:
                        # TODO: BUG: we will have a problem here if 2 different boundary edges with bcs applied share a common node...
                        dirichlet_idxs.append(node_idxs)
                        dirichlet_vals.append(np.full(len(node_idxs), inlet.p_value, dtype=np.float64))
                case InletType.FLOW_RATE:
                    boundary_line_idxs = self.mesh.mesh_view.phys_boundary_name_to_boundary_line_idxs[boundary_name]
                    boundary_line_objs = [self.mesh.boundary_lines[i] for i in boundary_line_idxs]
                    tri_objs = [self.mesh.triangles[line.idx] for line in boundary_line_objs]
                    boundary_line_thicknesses = np.array([tri.h for tri in tri_objs])
                    boundary_line_lengths = np.array([line.length for line in boundary_line_objs])
                    boundary_flux_areas = boundary_line_thicknesses * boundary_line_lengths
                    total_area = np.sum(boundary_flux_areas)
                    node_pairs_idxs = self.mesh.mesh_view.boundary_line_idx_to_node_idxs[boundary_line_idxs] # gives 2 node idxs. At this point, node_pair_idxs (n_lines, 2) and line_lengths (n_lines, ) are in the same order - shape: (n_neumann_lines, 2)
                    neumann_vals_pairs = np.repeat(boundary_flux_areas/2, 2) * (inlet.q_value/total_area)
                    neumann_vals_pairs = neumann_vals_pairs.reshape(len(node_pairs_idxs), 2)
                    if inlet.is_open:
                        neumann_idxs_pairs.append(node_pairs_idxs)
                        neumann_vals_per_idx_pair.append(neumann_vals_pairs)
                    print("Note: Flow rate BC is experimental.")
                case _:
                    pass
        # TODO: do this following assertion a little better...
        try:
            if len(dirichlet_idxs) > 0:
                self.bcs.dirichlet_idx = np.concatenate(dirichlet_idxs)
                self.bcs.dirichlet_vals = np.concatenate(dirichlet_vals)
            if len(neumann_idxs_pairs) > 0:
                self.bcs.neumann_idx = np.concatenate(neumann_idxs_pairs).flatten()
                self.bcs.neumann_vals = np.concatenate(neumann_vals_per_idx_pair).flatten()
        except ValueError:
            raise ConfigurationError("No inlets are currently open. At least one inlet must be open at all times to allow resin to flow into the part.")
        
        # assign vacuum vent pressure if vent exists
        if len(self.gates_manager._assigned_vents) > 0:
            vent_obj = next(iter(self.gates_manager._assigned_vents.values()))
            self.bcs.p0_val = vent_obj.vacuum_pressure
        else:
            self.bcs.p0_val = 0.0

    def get_empty_nodes_idx(self, fill_factor):
        """
        Complementary to "update_bcs()", this updates the indices of all nodes with a fill factor < 1.0. These will be uses to assign an internal condition p=0.
        """
        return np.where(fill_factor < 1.0)[0]

    # TODO:IMPORTANT this must be updated for neumann
    def fill_initial_cvs(self):
        """
        Must be called AFTER calling "update_bcs()"
        """
        self.solver_vars["fill_factor_array"][self.bcs.dirichlet_idx] = 1
        self.solver_vars["fill_factor_array"][self.bcs.neumann_idx] = 1


    
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
        self.current_time = 0
        self.time_step_counter = 0
        self.next_wo_time = self.simulation_parameters.output_interval
        self.solver_vars["fill_factor_array"] = np.zeros(self.N_nodes)
        self.bcs = SolverBCs()
        self.mesh.empty_cvs()
        self.gates_manager.reset_inlets()
        self.update_bcs()
        self.fill_initial_cvs()
        p0_idxs = self.get_empty_nodes_idx(self.solver_vars["fill_factor_array"])
        self.n_empty_cvs = len(p0_idxs)
        self.bcs.p0_idx = p0_idxs
        active_cvs_ids, self.solver_vars["free_surface_array"] = self.fill_solver.find_free_surface_cvs(
            self.solver_vars["fill_factor_array"], self.cv_support_cvs_array)
        self.time_step_manager.reset()
        initial_time_step = self.generate_initial_time_step()
        self.time_step_manager.save_timestep(*initial_time_step)
        self._sensor_manager.reset_sensors()
        # TODO: this first probe is temporary and should be cleaner
        self._sensor_manager.probe_current_solution(self.time_step_manager.p_buffer[0], self.time_step_manager.v_nodal_buffer[0], self.time_step_manager.fill_factor_buffer[0], 0.0)
        self.time_step_counter += 1

    def handle_wo_criterion(self, dt):
        write_out = False
        next_time = self.current_time + dt

        if next_time > self.step_end_time:
            dt = self.step_end_time - self.current_time
            write_out = True
            self.step_completed = True
            return dt, write_out
        
        if self.simulation_parameters.output_interval > 0.0:
            if next_time > self.next_wo_time:
                dt = self.next_wo_time - self.current_time
                self.next_wo_time += self.simulation_parameters.output_interval
                write_out = True
        else:
            write_out = True
            
        return dt, write_out

    def handle_wo_by_sensor_triggered(self, current_write_out, fill_factor_array):
        write_out = current_write_out
        triggered = self._sensor_manager.check_for_new_sensor_triggered(fill_factor_array)
        if triggered:
            write_out = True
            self.step_completed = True
        return write_out

    def solve_time_step(self, lightweight=False):
        fill_factor = self.solver_vars["fill_factor_array"]
        free_surface = self.solver_vars["free_surface_array"]
        cv_volumes = self.solver_vars["cv_volumes_array"]

        neumann_idxs = self.bcs.neumann_idx
        neumann_vals = self.bcs.neumann_vals
        f_neumann = self.f_orig.copy()
        for i in range(len(neumann_idxs)):
            f_neumann[neumann_idxs[i]] += neumann_vals[i]
        p = PressureSolver.solve_with_mask(
            self.K_sing, f_neumann, self.bcs, 
            self.solver_type, tol=self.solver_tol,
            max_iter=self.solver_max_iter, verbose=self.solver_verbose,
            **self.solver_kwargs)

        v_array = self.vsolver.calculate_elem_velocities(p, self.material_manager.assigned_resin.mu)
        v_nodal_array = np.zeros((self.N_nodes, 3))

        active_cvs_ids, free_surface = self.fill_solver.find_free_surface_cvs(fill_factor, self.cv_support_cvs_array)
        dt = self.fill_solver.calculate_time_step(active_cvs_ids, fill_factor, cv_volumes, v_array)
        dt, write_out = self.handle_wo_criterion(dt)

        fill_factor = self.fill_solver.fill_current_time_step(active_cvs_ids, fill_factor, cv_volumes, dt, self.simulation_parameters.fill_tolerance)

        # Update the filling time
        self.current_time += dt

        if self.simulation_parameters.end_step_when_sensor_triggered:
            write_out = self.handle_wo_by_sensor_triggered(write_out, fill_factor)
        # update the empty nodes idxs and count for next step
        p0_idxs = self.get_empty_nodes_idx(fill_factor)
        self.n_empty_cvs = len(p0_idxs)
        self.bcs.p0_idx = p0_idxs
        # always save and probe the final timestep
        if self.n_empty_cvs == 0:
            write_out = True
        if write_out:
            if not lightweight:
                self.time_step_manager.save_timestep(self.time_step_counter, self.current_time, dt, p, v_array, v_nodal_array, fill_factor, free_surface)
            self._sensor_manager.probe_current_solution(p, v_nodal_array, fill_factor, self.current_time)
        self.time_step_counter += 1

    def solve(self, log="on", lightweight=False):
        solution = None
        solve_time_start = time.time()
        self.step_end_time = np.inf  # reset step end time for full solve
        print("SOLVE STARTED for mesh with {} elements".format(len(self.mesh.triangles)))
        self.update_bcs()
        while self.n_empty_cvs > 0:
            self.solve_time_step()
            if log == "on":
                print("\rFill time: {:.2f}".format(self.current_time) + "s, Empty CVs: {:4}".format(self.n_empty_cvs), end='')
        if not lightweight:
            solution = self.time_step_manager.pack_solution()
        # good night and good luck
        solve_time_end = time.time()
        total_solve_time = solve_time_end - solve_time_start
        print("\nSOLVE COMPLETED in {:.2f} seconds".format(total_solve_time))
        return solution

    def solve_time_interval(self, time_interval:float, log="off", lightweight=False):
        solution = None
        self.step_completed = False
        self.step_end_time = self.current_time + time_interval
        solve_time_start = time.time()
        while self.step_completed == False and self.n_empty_cvs > 0:
            self.update_bcs()
            self.solve_time_step(lightweight=lightweight)
            if log == "on":
                print("\rFill time: {:.2f}".format(self.current_time) + "s, Empty CVs: {:4}".format(self.n_empty_cvs),
                      end='')
        if not lightweight:
            solution = self.time_step_manager.pack_solution()
        solve_time_end = time.time()
        total_solve_time = solve_time_end - solve_time_start
        return solution