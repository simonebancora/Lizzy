#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import time
from lizzy.solver import *
from lizzy.bcond.bcond import SolverBCs

class Solver:
    def __init__(self, mesh, bc_manager, simulation_parameters, material_manager, sensor_manager, solver_type=SolverType.DIRECT_SPARSE):
        self.mesh = mesh
        self.bc_manager = bc_manager
        self.simulation_parameters = simulation_parameters
        self.material_manager = material_manager
        self.time_step_manager = TimeStepManager()
        self._sensor_manager = sensor_manager
        self.bcs = SolverBCs()
        self.vsolver = None
        self.solver_type = solver_type
        self.N_nodes = mesh.nodes.N
        self.K_sing = None
        self.f_orig = None
        self.K_sol = None
        self.f_sol = None
        self.new_step_dofs = []
        self.current_time = 0
        self.n_empty_cvs = np.inf
        self.next_wo_time = self.simulation_parameters.wo_delta_time
        self.wo_by_sensor_triggered = False
        self.step_end_time = np.inf
        self.step_completed = False
        self.k_local_all = np.empty((self.mesh.triangles.N, 6))
        self.f_local_all = np.zeros((self.mesh.triangles.N, 3))
        self.solver_vars = {"fill_factor_array" : np.empty(self.N_nodes),
                            "filled_node_ids" : [],
                            "free_surface_array" : np.empty(self.N_nodes),
                            "cv_volumes_array" : np.empty(self.N_nodes),}
        self.cv_support_cvs_array = {}
        self.perform_fe_precalcs()
        self.compute_k_local()
        # when a solver is instantiated, all simulation variables are initialised
        self.initialise_new_solution()

    def perform_fe_precalcs(self):
        if not self.mesh.preprocessed:
            self.mesh.preprocess(self.material_manager)
        if not self.simulation_parameters.has_been_assigned:
            print(f"Warning: Simulation parameters were not assigned. Running with default values: mu={self.simulation_parameters.mu}, wo_delta_time={self.simulation_parameters.wo_delta_time}")
        # assemble FE global matrix (singular)
        self.K_sing, self.f_orig = fe.Assembly(self.mesh, self.simulation_parameters.mu)
        # TODO: reorder nodes here to reduce bandwidth - then reorder the whole mesh and objects

        self.vsolver = VelocitySolver(self.mesh.triangles)
        # precalculate vectorised version of all variables
        fill_factor_list = []
        cv_volumes_list = []
        for cv in self.mesh.CVs:
            fill_factor_list.append(cv.fill)
            cv_volumes_list.append(cv.vol)
            self.cv_support_cvs_array[cv.id] = np.array([support_cv.id for support_cv in cv.support_CVs])
        self.solver_vars["fill_factor_array"] = np.array(fill_factor_list, dtype=float)
        self.solver_vars["cv_volumes_array"] = np.array(cv_volumes_list, dtype=float)
        # assign sensors
        self._sensor_manager.initialise(self.mesh)

    def update_dirichlet_bcs(self):
        dirichlet_idx = []
        dirichlet_vals = []
        for tag, inlet in self.bc_manager.assigned_inlets.items():
            try:
                inlet_idx = self.mesh.boundaries[tag]
            except KeyError:
                raise KeyError(f"Mesh does not contain physical tag: {tag}")
            dirichlet_idx.append(inlet_idx)
            dirichlet_vals.append(np.ones(len(inlet_idx)) * inlet.p_value)
        self.bcs.dirichlet_idx = np.concatenate(dirichlet_idx)
        self.bcs.dirichlet_vals = np.concatenate(dirichlet_vals)


    def update_empty_nodes_idx(self):
        """
        Complementary to "update_dirichlet_bcs()", this updates the indices of all nodes with a fill factor < 1.0. These will be uses to assign an internal condition p=0.
        """
        # empty_node_ids = [cv.id for cv in self.mesh.CVs if cv.fill < 1]  # nodes with fill factor < 1
        empty_node_ids = np.where(self.solver_vars["fill_factor_array"] < 1.0)[0]
        self.bcs.p0_idx = np.array(empty_node_ids)

    def fill_initial_cvs(self):
        """
        Must be called AFTER calling "update_dirichlet_bcs()"
        """
        # initial_cvs = self.mesh.CVs[self.bcs.dirichlet_idx]
        self.solver_vars["fill_factor_array"][self.bcs.dirichlet_idx] = 1
        # for cv in initial_cvs:
        #     cv.fill = 1.0

    def update_n_empty_cvs(self):
        """
        Must be called AFTER calling "update_empty_nodes_idx()"
        """
        self.n_empty_cvs = len(self.bcs.p0_idx)

    def initialise_new_solution(self):
        """
        Initialises a new solution, resetting all simulation variables. It is sufficient to call this method to reset the simulation and run again.
        """
        self.current_time = 0
        self.next_wo_time = self.simulation_parameters.wo_delta_time
        self.solver_vars["fill_factor_array"] = np.zeros(self.N_nodes)
        self.bcs = SolverBCs()
        self.mesh.EmptyCVs()
        self.bc_manager.reset_inlets()
        self.update_dirichlet_bcs()
        self.fill_initial_cvs()
        self.update_empty_nodes_idx()
        self.update_n_empty_cvs()
        # self.K_sol, self.f_sol = PressureSolver.apply_starting_bcs(self.K_sing, self.f_orig, self.bcs)
        self.new_step_dofs = []
        self.solver_vars["filled_node_ids"] = np.where(self.solver_vars["fill_factor_array"] >= 1)[0]
        active_cvs_ids, self.solver_vars["free_surface_array"] = FillSolver.find_free_surface_cvs(
            self.solver_vars["fill_factor_array"], self.cv_support_cvs_array)
        self.time_step_manager.reset()
        self.time_step_manager.save_initial_timestep(self.mesh, self.bcs)
        self._sensor_manager.reset_sensors()
        # TODO: this first probe is temporary and should be cleaner
        self._sensor_manager.probe_current_solution(self.time_step_manager.time_steps[0].P, self.time_step_manager.time_steps[0].V_nodal, self.time_step_manager.time_steps[0].fill_factor, 0.0)

    def handle_wo_criterion(self, dt):
        write_out = False
        next_time = self.current_time + dt
        if next_time > self.step_end_time:
            dt = self.step_end_time - self.current_time
            write_out = True
            self.step_completed = True
            return dt, write_out
        if self.simulation_parameters.wo_delta_time > 0.0:
            if next_time > self.next_wo_time:
                dt = self.next_wo_time - self.current_time
                self.next_wo_time += self.simulation_parameters.wo_delta_time
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
            print("\nSensor triggered")
        return write_out

    def compute_k_local(self):
        for i, tri in enumerate(self.mesh.triangles):
            mu = self.simulation_parameters.mu
            k_el = tri.grad_N.T @ tri.k @ tri.grad_N * tri.A * tri.h / mu
            self.k_local_all[i, 0] = k_el[0,0]
            self.k_local_all[i, 1] = k_el[1,1]
            self.k_local_all[i, 2] = k_el[2,2]
            self.k_local_all[i, 3] = k_el[0,1]
            self.k_local_all[i, 4] = k_el[0,2]
            self.k_local_all[i, 5] = k_el[1,2]

    def update_and_collect_solver_input(self):
        dirichlet_idx_full = np.concatenate((self.bcs.dirichlet_idx, self.bcs.p0_idx), axis=None)
        dirichlet_vals_full = np.concatenate((self.bcs.dirichlet_vals, np.zeros((1, len(self.bcs.p0_idx)))), axis=None)

        mask_nodes = self.solver_vars["free_surface_array"].copy()
        mask_nodes[self.solver_vars["filled_node_ids"]] = 1

        elem_connectivity = self.mesh.mesh_data["nodes_conn"] # reference - ok

        mask_elements = np.zeros(self.mesh.triangles.N)
        for i, node_ids in enumerate(elem_connectivity):
            for node_id in node_ids:
                if node_id in self.solver_vars["filled_node_ids"]:
                    mask_elements[i] = 1
                    break



        return self.k_local_all, self.f_local_all, dirichlet_idx_full, dirichlet_vals_full, mask_nodes, mask_elements, self.new_step_dofs, elem_connectivity


    def solve_time_step(self):
        k_local_all, f_local_all, dirichlet_idx_full, dirichlet_vals_full, mask_nodes, mask_elements, new_dofs_added, elem_connectivity = self.update_and_collect_solver_input()
        k, f = PressureSolver.apply_bcs(self.K_sing, self.f_orig, self.bcs)
        # self.K_sol, self.f_sol = PressureSolver.free_dofs(self.K_sol, self.f_sol, self.K_sing, self.f_orig, self.new_step_dofs)
        p = PressureSolver.solve(k, f, self.solver_type)

        v_array = self.vsolver.calculate_elem_velocities(p, self.simulation_parameters.mu)
        v_nodal_array = self.vsolver.calculate_nodal_velocities(self.mesh.nodes, v_array)

        active_cvs_ids, self.solver_vars["free_surface_array"] = FillSolver.find_free_surface_cvs(self.solver_vars["fill_factor_array"], self.cv_support_cvs_array)
        dt = FillSolver.calculate_time_step(active_cvs_ids, self.solver_vars["fill_factor_array"], self.solver_vars["cv_volumes_array"], v_array)
        dt, write_out = self.handle_wo_criterion(dt)

        self.solver_vars["fill_factor_array"] = FillSolver.fill_current_time_step(active_cvs_ids, self.solver_vars["fill_factor_array"], self.solver_vars["cv_volumes_array"], dt, self.simulation_parameters.fill_tolerance)

        # find the newly filled cv ids as difference from the previous step
        current_filled_node_ids = np.where(self.solver_vars["fill_factor_array"] >= 1)[0]
        self.new_step_dofs = [id for id in current_filled_node_ids if id not in self.solver_vars["filled_node_ids"]]
        self.solver_vars["filled_node_ids"] = current_filled_node_ids

        # Update the filling time
        self.current_time += dt
        # save time step results
        fill_factor = [cv.fill for cv in self.mesh.CVs]
        if self.wo_by_sensor_triggered:
            write_out = self.handle_wo_by_sensor_triggered(write_out, fill_factor)
        self.time_step_manager.save_timestep(self.current_time, dt, p, v_array, v_nodal_array, self.solver_vars["fill_factor_array"], self.solver_vars["free_surface_array"], write_out)
        if write_out:
            self._sensor_manager.probe_current_solution(p, v_nodal_array, self.solver_vars["fill_factor_array"], self.current_time)
        # update the empty nodes for next step
        self.update_empty_nodes_idx()
        # Print number of empty cvs
        self.update_n_empty_cvs()



    def solve(self, log="on"):
        solve_time_start = time.time()
        print("SOLVE STARTED for mesh with {} elements".format(self.mesh.triangles.N))
        while self.n_empty_cvs > 0:
            self.solve_time_step()
            if log == "on":
                print("\rFill time: {:.5f}".format(self.current_time) + ", Empty CVs: {:4}".format(self.n_empty_cvs), end='')
        solution = self.time_step_manager.pack_solution()
        # good night and good luck
        solve_time_end = time.time()
        total_solve_time = solve_time_end - solve_time_start
        print("\nSOLVE COMPLETED in {:.2f} seconds".format(total_solve_time))
        return solution

    def solve_step(self, step_period, log="off", lightweight=False):
        self.step_completed = False
        self.step_end_time = self.current_time + step_period
        solve_time_start = time.time()
        # print("STEP SOLVE STARTED for mesh with {} elements".format(self.mesh.triangles.N))
        while self.step_completed == False and self.n_empty_cvs > 0:
            self.update_dirichlet_bcs()
            self.solve_time_step()
            if log == "on":
                print("\rFill time: {:.5f}".format(self.current_time) + ", Empty CVs: {:4}".format(self.n_empty_cvs),
                      end='')
        if lightweight:
            solution = "Lightweight mode: no solution is saved"
        else:
            solution = self.time_step_manager.pack_solution()
        # good night and good luck
        solve_time_end = time.time()
        total_solve_time = solve_time_end - solve_time_start
        # print("\nSTEP SOLVE COMPLETED in {:.2f} seconds".format(total_solve_time))
        return solution
    
