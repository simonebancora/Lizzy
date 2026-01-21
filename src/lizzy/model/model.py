#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.sensors import Sensor
    from lizzy._core.materials import PorousMaterial, Rosette
    from lizzy._core.bcond.gates import Inlet

from typing import Dict, Literal
from types import MappingProxyType
from lizzy._core.io import Reader, Writer
from lizzy._core.cvmesh import Mesh
from lizzy._core.bcond import BCManager
from lizzy._core.solver import Solver, SolverType
from lizzy._core.sensors import SensorManager
from lizzy._core.datatypes import SimulationParameters
from lizzy._core.materials import MaterialManager
from lizzy.utils.splash_logo import print_logo


class LizzyModel:
    """
    The main class for defining simulations in Lizzy. This class wraps all subcomponents of the solver and exposes all user-facing APIs. Provides access to methods for reading a mesh, assigning properties, configuring the solver, saving results and more. A script typically begins with the instantiation of a LizzyModel.
    """
    def __init__(self):
        print_logo()
        self._reader : Reader = None
        self._writer : Writer = None
        self._mesh : Mesh = None
        self._solver : Solver = None
        self._renderer : any = None
        self._latest_solution: dict = None
        self._simulation_parameters = SimulationParameters()
        self._material_manager = MaterialManager()
        self._bc_manager = BCManager()
        self._sensor_manager = SensorManager()
        self._lightweight = False

    @property
    def lightweight(self):
        r"""Set whether to run the model in lightweight mode. Default is False.

        When the model is run in lighweight mode, solver results are not serialised at the end of steps into solution output format and :func:`~LizzyModel.save_results` cannot be called. Useful to speed up computation when saving results to an output file is not necessary
        
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

    def print_simulation_parameters(self) -> None:
        """
        Print the currently assigned simulation parameters.
        """
        self._simulation_parameters.print_current()
    
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


    def assign_simulation_parameters(self, **kwargs):
        r"""
        Assigns new values to one or more simulation parameters using keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments corresponding to parameter names and their new values.
            Valid parameters are:
        
            - ``mu``: viscosity [Pa s]
            - ``wo_delta_time``: interval of simulation time between solution write-outs [s]. Default: -1 (write-out every numerical time step)
            - ``fill_tolerance``: tolerance on the fill factor to consider a CV as filled. Default: 0.01
            - ``end_step_when_sensor_triggered``: if True, ends current solution step and creates a write-out when a sensor changes state. Default: False
        
        Examples
        --------
        >>> model.assign_simulation_parameters(mu=0.2, wo_delta_time=50)
        

        Raises
        ------
        AttributeError
            If any key in `kwargs` does not correspond to a known attribute.
        """
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

    def create_material(self, k1: float, k2: float, k3: float, porosity: float, thickness: float, name:str= None) -> PorousMaterial:
        """Create a new material that can then be selected and used in the model.

        Parameters
        ----------
        k1 : float
            Permeability in the first principal direction.
        k2 : float
            Permeability in the second principal direction.
        k3 : float
            Permeability in the third principal direction.
        porosity : float
            Volumetric porosity of the material (porosity = 1 - fibre volume fraction).
        thickness : float
            Thickness of the material [mm].
        name : str, optional
            Label assigned to the material. Necessary to select the material during assignment. If none assigned, a default 'Material_{N}'name is given, where N is an incremental number of existing materials.

        Returns
        -------
        :class:`~lizzy.core.materials.PorousMaterial`
            Instance of the created material.
        """
        new_material = self._material_manager.create_material(k1, k2, k3, porosity, thickness, name)
        return new_material

    def assign_material(self, material_selector, mesh_tag:str, rosette:Rosette = None):
        """Assign an existing material to a labeled mesh region.

        Parameters
        ----------
        material_selector : str
            Label of the material to assign. Must correspond to an existing material created with `LizzyModel.create_material`.
        mesh_tag : str
            Label of the mesh region where to assign the material.
        rosette : Rosette, optional
            Orientation rosette to apply to the material. If none provided, a default rosette with k1 aligned with the global X axis is assigned.
        """
        self._material_manager.assign_material(material_selector, mesh_tag, rosette)

    def create_rosette(self, p1:tuple[float, float, float], p0:tuple[float, float, float]=(0.0,0.0,0.0), name:str=None) -> Rosette:
        """Create a new rosette that can then be selected and used in the model.

        Parameters
        ----------
        p1 : tuple[float, float, float]
            The first point defining the first axis of the rosette (k1 direction).
        p0 : tuple[float, float, float]
            The second point defining the first axis of the rosette (k1 direction). Default is (0,0,0).
        name : str, optional
            Label assigned to the rosette. Necessary to select the rosette during assignment. If none assigned, a default 'Rosette_{N}'name is given, where N is an incremental number of existing rosettes.

        Returns
        -------
        :class:`~lizzy.core.materials.Rosette`
            Instance of the created rosette.
        """
        new_rosette = self._material_manager.create_rosette(p1, p0, name)
        return new_rosette

    def create_inlet(self, initial_pressure_value:float, name:str = None) -> Inlet:
        """Creates a new inlet and add it to model existing inlets.

        Parameters
        ----------
        initial_pressure_value : float
            Initial pressure value at the inlet.
        name : str, optional
            Label assigned to the inlet. Will be used to select the inlet in future operations. If none assigned, a default 'Inlet_{N}'name is given, where N is an incremental number of existing inlets.

        Returns
        -------
        :class:`~lizzy.core.bcond.Inlet`
            The created inlet object.
        """
        new_inlet = self._bc_manager.create_inlet(initial_pressure_value, name)
        return new_inlet

    def assign_inlet(self, inlet_selector:Inlet | str, boundary_tag:str):
        """Selects an inlet from existing ones and assigns it to the indicated mesh boundary.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        boundary_tag : str
            An existing mesh boundary tag where to assign the inlet.
        """
        self._bc_manager.assign_inlet(inlet_selector, boundary_tag)
    
    def fetch_inlet_by_name(self, inlet_name: str) -> Inlet:
        """Fetches an inlet from existing ones in the model.

        Parameters
        ----------
        inlet_name :  str
            The name of an existing inlet.

        Returns
        -------
        :class:`~lizzy.gates.Inlet`
            The fetched inlet object.
        """
        selected_inlet = self._bc_manager._fetch_inlet(inlet_name)
        return selected_inlet
    
    def change_inlet_pressure(self, inlet_selector:Inlet | str, pressure_value:float, mode: Literal["set", "delta"] = "set"):
        """Changes the pressure value at the selected inlet to a new value, according to the selected mode.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        pressure_value : float
            The new pressure value to set at the inlet.
        mode : {'set', 'delta'}, optional
            How to apply the new pressure value:

            - ``set`` (default): directly set the new pressure value.
            - ``delta``: increment the existing pressure by the given value.
        Raises
        ------
        KeyError
            If the `mode` is not one of the allowed values.
        """
        self._bc_manager.change_inlet_pressure(inlet_selector, pressure_value, mode)

    def open_inlet(self, inlet_selector:Inlet | str):
        """Sets the selected inlet state to `open`. When open, the inlet applies its p_value as a Dirichlet boundary condition. An inlet can be opened at any time during the simulation.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object reference, or the name of an existing inlet.
        """
        self._bc_manager.open_inlet(inlet_selector)

    def close_inlet(self, inlet_selector:Inlet | str):
        """Sets the selected inlet state to `closed`. When closed, the inlet acts as a Neumann natural boundary condition (no flux). An inlet can be closed at any time during the simulation. The stored p_value is preserved when the inlet is closed.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object reference, or the name of an existing inlet.
        """
        self._bc_manager.close_inlet(inlet_selector)

    #TODO: get coords arg as tuple or np array, then ids as int or string
    def create_sensor(self, x:float, y:float, z:float):
        """Create a virtual sensor at the specified position and add it to the model.

        Parameters
        ----------
        x : float
            The x coordinate of the sensor
        y : float
            The y coordinate of the sensor
        z : float
            The z coordinate of the sensor
        """
        self._sensor_manager.add_sensor(x, y, z)

    def print_sensor_readings(self):
        """Prints to the console the current values of :attr:`~lizzy.sensors.Sensor.time`, :attr:`~lizzy.sensors.Sensor.pressure`, :attr:`~lizzy.sensors.Sensor.fill_factor` and :attr:`~lizzy.sensors.Sensor.velocity` of each sensor.
        """
        self._sensor_manager.print_sensor_readings()

    def get_sensor_trigger_states(self) -> list[bool]:
        """Returns a list of sensor trigger states: True if the sensor has been triggered, False otherwise."""
        return self._sensor_manager.sensor_trigger_states
    
    def get_sensor_by_id(self, idx)  -> Sensor:
        """Fetches a sensor by its index.
        """
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

    def solve(self, log="on") -> dict:
        """Advance the filling simulation from the current time until the part is filled.

        Parameters
        ----------
        log : str, optional
            Whether to print the progress of the solution, by default "on"

        Returns
        -------
        solution : dict
            A dictionary containing the solution.
        """
        self._latest_solution = self._solver.solve(log=log)
        return self._latest_solution

    def solve_time_interval(self, time_interval:float, log="off") -> dict:
        """Advance the filling simulation from the current time for the specified time interval.

        Parameters
        ----------
        time_interval : float
            The time period to advance the simulation for.
        log : str, optional
            Whether to print the progress of the solution, by default "off"

        Returns
        -------
        solution : dict
            A dictionary containing the solution up to the time step reached.
        """
        self._latest_solution = self._solver.solve_time_interval(time_interval, log=log, lightweight=self._lightweight)
        return self._latest_solution
    
    def initialise_new_solution(self):
        """
        Initialises a new solution, resetting all simulation variables. The part will be emptied and initial boundary conditions restored. This method can be called to reset a simulation and run a new one, without resetting the model.
        """
        self._solver.initialise_new_solution()
    
    def save_results(self, solution:dict, result_name:str, **kwargs):
        """Save the results contained in the solution dictionary into an XDMF file.

        Parameters
        ----------
        solution : dict
        result_name : str
            The name of the new folder where results will be saved.
        """
        self._writer.save_results(solution, result_name, **kwargs)

    def get_node_by_id(self, node_id:int):
        return self._mesh.nodes[node_id]






