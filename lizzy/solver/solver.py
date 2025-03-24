#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
import time
from lizzy.solver import *
from lizzy.bcond import SolverBCs
from lizzy.simparams import ProcessParameters

class Solver:
    def __init__(self, mesh, bc_manager, solver_type=SolverType.DIRECT_SPARSE):
        """
        The Solver object performs all FE/CV calculations to simulate the filling. Must be instantiated for a solution to be calculated.

        Parameters
        ----------
        mesh : lizzy.mesh.Mesh
            Lizzy mesh object that provides the calculation domain.
        bc_manager : lizzy.bcond.BCManager
            The manager that contains all boundary conditions to be used for the solution.
        solver_type : lizzy.solver.SolverType
            Currently implemented solvers are DIRECT_DENSE and DIRECT_SPARSE.
        """
        self.mesh = mesh
        self.bc_manager = bc_manager
        self.bcs = SolverBCs()
        self.solver_type = solver_type
        self.N_nodes = mesh.nodes.N
        self.K_sing = None
        self.f_orig = None
        self.current_time = 0
        self.n_empty_cvs = np.inf
        self.next_wo_time = ProcessParameters.wo_delta_time
        # assembly is calculated at instantiation of the solver
        self.perform_fe_precalcs()
        # when a solver is instantiated, all simulation variables are initialised
        self.initialise_new_solution()

    def perform_fe_precalcs(self):
        # assemble FE global matrix (singular)
        self.K_sing, self.f_orig = fe.Assembly(self.mesh, ProcessParameters.mu)
        # precalculate vectorised stuff for velocity
        VelocitySolver.precalculate_B(self.mesh.triangles)

    def update_dirichlet_bcs(self):
        """
        Very important method. updates 2 arrays of matching elements:
            - the indices of the nodes where a boundary dirichlet value is applied
            - the values applied to the nodes
        """
        dirichlet_idx = []
        dirichlet_vals = []
        for inlet in self.bc_manager.inlets:
            try:
                inlet_idx = self.mesh.boundaries[inlet.physical_tag]
            except KeyError:
                raise KeyError(f"Mesh does not contain physical tag: {inlet.physical_tag}")
            dirichlet_idx.append(inlet_idx)
            dirichlet_vals.append(np.ones(len(inlet_idx)) * inlet.p_value)
        self.bcs.dirichlet_idx = np.concatenate(dirichlet_idx)
        self.bcs.dirichlet_vals = np.concatenate(dirichlet_vals)

    def update_empty_nodes_idx(self):
        """
        Complementary to "update_dirichlet_bcs()", this updates the indices of all nodes with a fill factor < 1.0. These will be uses to assign an internal condition p=0.
        """
        empty_node_ids = [cv.id for cv in self.mesh.CVs if cv.fill < 1]  # nodes with fill factor < 1
        self.bcs.p0_idx = np.array(empty_node_ids)

    def fill_initial_cvs(self):
        """
        Must be called AFTER calling "update_dirichlet_bcs()"
        """
        initial_cvs = self.mesh.CVs[self.bcs.dirichlet_idx]
        for cv in initial_cvs:
            cv.fill = 1.0

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
        self.next_wo_time = ProcessParameters.wo_delta_time
        self.bcs = SolverBCs()
        self.mesh.EmptyCVs()
        self.update_dirichlet_bcs()
        self.fill_initial_cvs()
        self.update_empty_nodes_idx()
        self.update_n_empty_cvs()
        TimeStepManager.reset()
        TimeStepManager.save_initial_timestep(self.mesh, self.bcs)

    def solve(self, log="on"):
        solve_time_start = time.time()
        print("SOLVE STARTED for mesh with {} elements".format(self.mesh.triangles.N))
        while self.n_empty_cvs > 0:
            write_out = False
            # Solve pressure field
            k, f = PressureSolver.apply_bcs(self.K_sing, self.f_orig, self.bcs)
            p = PressureSolver.solve(k, f, self.solver_type)
            # calculate velocity field
            v_array = VelocitySolver.calculate_elem_velocities(p, ProcessParameters.mu)
            # Find active cvs on the free surface
            active_cvs = FillSolver.find_free_surface_cvs(self.mesh.CVs)
            # Calculate current time step for filling active cvs
            dt = FillSolver.calculate_time_step(active_cvs, v_array)
            # if dt passes a scheduled write-out time, force dt to match the write-out time and flag the step for write-out
            if ProcessParameters.wo_delta_time > 0.0:
                if self.current_time + dt > self.next_wo_time:
                    dt = self.next_wo_time - self.current_time
                    self.next_wo_time += ProcessParameters.wo_delta_time
                    write_out = True
            else:
                write_out = True
            # Fill active cvs
            FillSolver.fill_current_time_step(active_cvs, dt)
            # Update the filling time
            self.current_time += dt
            # save time step results
            TimeStepManager.save_timestep(self.current_time, dt, p, v_array, [cv.fill for cv in self.mesh.CVs], [cv.free_surface for cv in self.mesh.CVs], write_out)
            # update the empty nodes for next step
            self.update_empty_nodes_idx()
            # Print number of empty cvs
            self.update_n_empty_cvs()
            if log == "on":
                print("\rFill time: {:.5f}".format(self.current_time) + ", Empty CVs: {:4}".format(self.n_empty_cvs), end='')

        solution = TimeStepManager.pack_solution()
        # good night and good luck
        solve_time_end = time.time()
        total_solve_time = solve_time_end - solve_time_start
        print("\nSOLVE COMPLETED in {:.2f} seconds".format(total_solve_time))
        return solution
    
