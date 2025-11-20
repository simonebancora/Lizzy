#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, overload
from lizzy.IO.IO import Reader, Writer
from lizzy.cvmesh.cvmesh import Mesh
from lizzy.materials import MaterialManager, PorousMaterial, Rosette
from lizzy.sensors.sensmanager import SensorManager
from lizzy.simparams import SimulationParameters
from lizzy.bcond.bcond import BCManager
from lizzy.solver.solver import Solver, SolverType

class LizzyModel:
    """
    The main class for defining simulations in Lizzy. This class wraps all subcomponents of the solver and exposes all user-oriented scripting APIs. Provides access to methods for reading a mesh, assigning properties, configuring the solver, saving results and more. A typical script begins with the instantiation of a LizzyModel.
    """
    def __init__(self):
        self._reader = None
        self._writer = None
        self._mesh = None
        self._solver = None
        self._renderer = None
        self._latest_solution: any = None
        self._simulation_parameters = SimulationParameters()
        self._material_manager = MaterialManager()
        self._bc_manager = BCManager()
        self._sensor_manager = SensorManager()
        self._lightweight = False

    @property
    def lightweight(self):
        r"""Set whether to run the model in lightweight mode. Default is ``False``.

        When the model is run in lighweight mode, solver results are not serialised at the end of steps into solution output format. If ``lightweight=True``, :func:`~LizzyModel.save_results` cannot be called. Useful to speed up computation when saving results to an output file is not necessary
        """
        return self._lightweight

    @lightweight.setter
    def lightweight(self, value):
        self._lightweight = value

    @property
    def assigned_materials(self) -> Dict[str, PorousMaterial]:
        return self._material_manager.assigned_materials

    @property
    def existing_materials(self) -> Dict[str, PorousMaterial]:
        return self._material_manager.existing_materials

    @property
    def n_empty_cvs(self) -> int:
        return self._solver.n_empty_cvs

    def get_number_of_empty_cvs(self) -> int:
        return self.n_empty_cvs

    @property
    def current_time(self) -> float:
        return self._solver.current_time

    def get_current_time(self) -> float:
        return self.current_time

    @property
    def latest_solution(self):
        return self._latest_solution

    def get_latest_solution(self) -> any:
        r"""
        Returns the most recent solution from the model. Returns None is the model is run in lightweight mode.
        :return: The solution at the latest time step.
        """
        return self.latest_solution

    @overload
    def assign_simulation_parameters(
            self,
            *,
            mu: float,
            wo_delta_time: float,
            fill_tolerance: float,
            has_been_assigned: bool,
            end_step_when_sensor_triggered: bool,
    ) -> None:
        r"""
        Assign several parameters of the simulation.
        ``mu``: viscosity [Pa s]
        ``wo_delta_time``: interval of simulation time between solution write-outs [s]
        ``fill_tolerance``: tolerance on the fill factor to consider a CV as filled. Default: 0.01
        ``end_step_when_sensor_triggered``: if True, ends current solution step and creates a write-out when a sensor changes state. Default: False
        """
        ...

    def assign_simulation_parameters(self, **kwargs):
        self._simulation_parameters.assign(**kwargs)

    def read_mesh_file(self, mesh_file_path:str):
        r"""
        Reads a mesh file and initialises the mesh. Currently only .MSH format is supported.
        :param mesh_file_path: Path to the mesh file.
        """
        self._reader = Reader(mesh_file_path)
        self._mesh = Mesh(self._reader)
        self._writer = Writer(self._mesh)

    def create_material(self, k1: float, k2: float, k3: float, porosity: float, thickness: float, name:str= None):
        new_material = self._material_manager.create_material(k1, k2, k3, porosity, thickness, name)
        return new_material

    def assign_material(self, material_selector, mesh_tag:str, rosette:Rosette = None):
        self._material_manager.assign_material(material_selector, mesh_tag, rosette)

    def create_inlet(self, initial_pressure_value:float, name:str = None):
        new_inlet = self._bc_manager.create_inlet(initial_pressure_value, name)
        return new_inlet

    def assign_inlet(self, inlet_selector, boundary_tag:str):
        self._bc_manager.assign_inlet(inlet_selector, boundary_tag)
    
    def change_inlet_pressure(self, inlet_selector, pressure_value:float, mode:str = "set"):
        self._bc_manager.change_inlet_pressure(inlet_selector, pressure_value, mode)

    def open_inlet(self, inlet_selector):
        self._bc_manager.open_inlet(inlet_selector)

    def close_inlet(self, inlet_selector):
        self._bc_manager.close_inlet(inlet_selector)

    def create_sensor(self, x:float, y:float, z:float, idx=None):
        self._sensor_manager.add_sensor(x, y, z, idx)

    def print_sensor_readings(self):
        self._sensor_manager.print_sensor_readings()

    def get_sensor_trigger_states(self):
        return self._sensor_manager.sensor_trigger_states
    
    def get_sensor_by_id(self, idx):
        return self._sensor_manager.get_sensor_by_id(idx)

    def initialise_solver(self, solver_type:SolverType = SolverType.DIRECT_SPARSE, 
                         solver_tol:float = 1e-8, solver_max_iter:int = 1000, 
                         solver_verbose:bool = False, use_masked_solver:bool = True,
                         **solver_kwargs):
        """
        Initialize the solver for the filling simulation.
        
        Parameters
        ----------
        solver_type : SolverType
            Type of linear solver (DIRECT_DENSE, DIRECT_SPARSE, ITERATIVE_PETSC).
            Default is DIRECT_SPARSE which is more efficient for sparse matrices.
        solver_tol : float
            Convergence tolerance for iterative solvers
        solver_max_iter : int
            Maximum iterations for iterative solvers
        solver_verbose : bool
            Print solver convergence information
        use_masked_solver : bool
            Use optimized masked solver (only solves for free DOFs). 
            Default is True for better performance (10-400x speedup in early timesteps).
        **solver_kwargs
            Additional solver-specific keyword arguments
        """
        self._solver = Solver(self._mesh, self._bc_manager, self._simulation_parameters, 
                            self._material_manager, self._sensor_manager, solver_type, 
                            solver_tol, solver_max_iter, solver_verbose, use_masked_solver,
                            **solver_kwargs)

    def solve(self):
        self._latest_solution = self._solver.solve()
        return self._latest_solution

    def solve_step(self, step_period:float):
        self._latest_solution = self._solver.solve_step(step_period, log="off", lightweight=self._lightweight)
        return self._latest_solution
    
    def initialise_new_solution(self):
        self._solver.initialise_new_solution()
    
    def save_results(self, solution, result_name:str):
        self._writer.save_results(solution, result_name)

    def get_node_by_id(self, node_id:int):
        return self._mesh.nodes[node_id]

# A bunch of getters
from lizzy.lizmodel.components import *





