#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, Literal, overload
from types import MappingProxyType
from lizzy.core.io import Reader, Writer
from lizzy.core.cvmesh import Mesh
from lizzy.core.bcond import BCManager
from lizzy.core.solver import Solver, SolverType
from lizzy.core.sensors import SensorManager
from .simparams import SimulationParameters
from lizzy.core.materials import MaterialManager, PorousMaterial, Rosette
from lizzy.utils.splash_logo import print_logo


class LizzyModel:
    """
    The main class for defining simulations in Lizzy. This class wraps all subcomponents of the solver and exposes all user-facing APIs. Provides access to methods for reading a mesh, assigning properties, configuring the solver, saving results and more. A script typically begins with the instantiation of a LizzyModel.
    """
    def __init__(self):
        print_logo()
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
        
        Note
        ----
        This property can be both read and set.
        """
        return self._lightweight

    @lightweight.setter
    def lightweight(self, value):
        self._lightweight = value

    @property
    def assigned_materials(self) -> Dict[str, PorousMaterial]:
        """Dictionary of assigned materials in the model. (read-only)
        """
        return MappingProxyType(self._material_manager.assigned_materials)

    @property
    def existing_materials(self) -> Dict[str, PorousMaterial]:
        """Dictionary of existing materials in the model. A material can be existing (after being created with :func:`~LizzyModel.create_material`) but not assigned to any mesh region. (read-only)
        """
        return MappingProxyType(self._material_manager.existing_materials)

    @property
    def n_empty_cvs(self) -> int:
        """
        Number of currently empty control volumes in the mesh (read-only).
        """
        return self._solver.n_empty_cvs

    @property
    def current_time(self) -> float:
        """
        Current simulation time from the start of the infusion (read-only).
        """
        return self._solver.current_time
    
    @property
    def latest_solution(self) -> dict:
        """The most recent solution from the model (read-only). This value is None is the model is run in `lightweight` mode.
        """
        return self._latest_solution
    
    @property
    def bc_manager(self) -> BCManager:
        return self._bc_manager
    
    @property
    def simulation_parameters(self) -> SimulationParameters:
        return self._simulation_parameters
    
    def get_number_of_empty_cvs(self) -> int:
        """
        Returns
        -------
        int:
            :attr:`~lizzy.LizzyModel.n_empty_cvs`
        """
        return self.n_empty_cvs

    def get_current_time(self) -> float:
        """
        Returns
        -------
        float
            :attr:`~lizzy.LizzyModel.current_time`
        """
        return self.current_time

    def get_latest_solution(self) -> Dict:
        """
        Returns
        -------
        dict
            :attr:`~lizzy.LizzyModel.latest_solution`
        """
        return self.latest_solution

    @overload
    def assign_simulation_parameters(
            self,
            *,
            mu: float,
            wo_delta_time: float,
            fill_tolerance: float,
            end_step_when_sensor_triggered: bool,
    ) -> None:
        ...

    def assign_simulation_parameters(self, **kwargs):
        self._simulation_parameters.assign(**kwargs)

    def read_mesh_file(self, mesh_file_path:str):
        r"""
        Reads a mesh file and initialises the mesh. Currently only .MSH format is supported (Version 4 ASCII).

        Parameters
        ----------
        mesh_file_path : str
            Path to the mesh file from the current working folder.
        """
        self._reader = Reader(mesh_file_path)
        self._mesh = Mesh(self._reader)
        self._writer = Writer(self._mesh)
    
    def print_mesh_info(self) -> None:
        """Prints some information about the mesh.
        """
        if not self._reader:
            print("Mesh data is empty. Please read a mesh file first.")
            return
        self._reader.print_mesh_info()

    def create_material(self, k1: float, k2: float, k3: float, porosity: float, thickness: float, name:str= None):
        """Wrapper for :meth:`~lizzy.core.materials.MaterialManager.create_material`
        """
        new_material = self._material_manager.create_material(k1, k2, k3, porosity, thickness, name)
        return new_material

    def assign_material(self, material_selector, mesh_tag:str, rosette:Rosette = None):
        """Wrapper for :meth:`~lizzy.core.materials.MaterialManager.assign_material`
        """
        self._material_manager.assign_material(material_selector, mesh_tag, rosette)
    
    def create_rosette(self, u:tuple[float, float, float], p0:tuple[float, float, float]=(0.0,0.0,0.0), name:str=None):
        """Wrapper for :meth:`~lizzy.core.materials.MaterialManager.create_rosette`
        """
        new_rosette = self._material_manager.create_rosette(u, p0, name)
        return new_rosette

    def create_inlet(self, initial_pressure_value:float, name:str = None):
        """Wrapper for :meth:`~lizzy.core.bcond.BCManager.create_inlet`
        """
        new_inlet = self._bc_manager.create_inlet(initial_pressure_value, name)
        return new_inlet

    def assign_inlet(self, inlet_selector, boundary_tag:str):
        """Wrapper for :meth:`~lizzy.core.bcond.BCManager.assign_inlet`
        """
        self._bc_manager.assign_inlet(inlet_selector, boundary_tag)
    
    def change_inlet_pressure(self, inlet_selector, pressure_value:float, mode: Literal["set", "delta"] = "set"):
        """Wrapper for :meth:`~lizzy.core.bcond.BCManager.change_inlet_pressure`
        """
        self._bc_manager.change_inlet_pressure(inlet_selector, pressure_value, mode)

    def open_inlet(self, inlet_selector):
        """Wrapper for :meth:`~lizzy.core.bcond.BCManager.open_inlet`"""
        self._bc_manager.open_inlet(inlet_selector)

    def close_inlet(self, inlet_selector):
        """Wrapper for :meth:`~lizzy.core.bcond.BCManager.close_inlet`"""
        self._bc_manager.close_inlet(inlet_selector)

    #TODO: get coords arg as tuple or np array, then ids as int or string
    def create_sensor(self, x:float, y:float, z:float, idx:int=None):
        """Create a virtual sensor at the specified position and add it to the model.

        Parameters
        ----------
        x : float
            The x coordinate of the sensor
        y : float
            The y coordinate of the sensor
        z : float
            The z coordinate of the sensor
        idx : int, optional
            The index of the sensor, by default None
        """
        self._sensor_manager.add_sensor(x, y, z)

    def print_sensor_readings(self):
        """Wrapper for :meth:`~lizzy.core.sensors.SensorManager.print_sensor_readings`"""
        self._sensor_manager.print_sensor_readings()

    def get_sensor_trigger_states(self):
        """Wrapper for :meth:`~lizzy.core.sensors.SensorManager.get_sensor_trigger_states`"""
        return self._sensor_manager.sensor_trigger_states
    
    def get_sensor_by_id(self, idx):
        """Wrapper for :meth:`~lizzy.core.sensors.SensorManager.get_sensor_by_id`"""
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
    
    def save_results(self, solution:dict, result_name:str, **kwargs):
        """Wrapper for :meth:`~lizzy.core.io.Writer.save_results`
        """
        self._writer.save_results(solution, result_name, **kwargs)

    def get_node_by_id(self, node_id:int):
        return self._mesh.nodes[node_id]






