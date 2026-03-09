#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.sensors import Sensor
    from lizzy._core.materials import PorousMaterial, Rosette, Resin
    from lizzy._core.gates.gates import Inlet, PressureInlet, FlowRateInlet, Vent
    from lizzy._core.cvmesh.entities import Node, Triangle
    from lizzy.datatypes import Solution

from typing import Dict, Literal
from types import MappingProxyType
from lizzy._core.io import Reader, Writer
from lizzy._core.cvmesh import Mesh
from lizzy._core.gates import GatesManager
from lizzy._core.solver import Solver, SolverType
from lizzy._core.sensors import SensorManager
from lizzy._core.datatypes import SimulationParameters
from lizzy._core.materials import MaterialManager
from lizzy.utils.splash_logo import print_logo
from lizzy.utils.decorators import State, preinit_only, postinit_only
from lizzy.exceptions import ConfigurationError

class LizzyModel:
    """
    The main class for defining simulations in Lizzy. This class wraps all subcomponents of the solver and exposes all user-facing APIs. Provides access to methods for reading a mesh, assigning properties, configuring the solver, saving results and more. A script typically begins with the instantiation of a LizzyModel.
    """
    def __init__(self):
        print_logo()
        self._model_name:str = None
        self._reader:Reader = None
        self._writer:Writer = None
        self._simulation_parameters:SimulationParameters = None
        self._material_manager:MaterialManager = None
        self._gates_manager:GatesManager = None
        self._sensor_manager:SensorManager = None
        self._mesh:Mesh = None
        self._solver:Solver = None
        self._latest_solution: Solution = None
        self._lightweight:bool = False
        self._state:State = State.PRE_INIT
        self._create_components()

    def _create_components(self):
        self._reader = Reader()
        self._writer = Writer()
        self._mesh = Mesh()
        self._simulation_parameters = SimulationParameters()
        self._material_manager = MaterialManager()
        self._gates_manager = GatesManager()
        self._sensor_manager = SensorManager()
    
    # ===========================================================================
    # Properties
    # ===========================================================================

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
    def latest_solution(self) -> Solution:
        """The most recent solution from the model (read-only). This value is None if the model is run in `lightweight` mode.
        """
        return self._latest_solution
    
    @property
    def gates_manager(self) -> GatesManager:
        return self._gates_manager
    
    # ===========================================================================
    # IO API
    # ===========================================================================

    @preinit_only
    def read_mesh_file(self, mesh_file_path:str):
        r"""
        Reads a mesh file and initialises the mesh. Currently only .MSH format is supported (Version 4 ASCII).

        Parameters
        ----------
        mesh_file_path : str
            Path to the mesh file from the current working folder.
        """
        self._reader.read_mesh_file(mesh_file_path)
        self._model_name = self._reader.case_name
        self._mesh.build_mesh(self._reader.mesh_data)
        
    def print_mesh_info(self) -> None:
        """Prints some information about the mesh.
        """
        if not self._reader:
            print("Mesh data is empty. Please read a mesh file first.")
            return
        self._reader.print_mesh_info()
    
    @postinit_only
    def save_results(self, solution: Solution = None, result_name:str = None, **kwargs):
        """Save the results contained in the solution dictionary into an XDMF file.

        Parameters
        ----------
        solution : :class:`~lizzy.datatypes.Solution`, optional
            The solution that should be written to the XDMF file. If none passed, the latest solution present in the model will be used.
        result_name : str, optional
            The name of the solution file that will be created. If none passed, the name of the mesh file with appended '_RES' will be used.
        """
        if self._lightweight:
            raise ConfigurationError(
                "save_results() cannot be called when the model is in lightweight mode. "
                "Set model.lightweight = False before solving to enable result serialisation."
            )
        if solution == None:
            solution = self._latest_solution
        if result_name == None:
            result_name = self._model_name + '_RES'
        self._writer.assign_mesh(self._mesh)
        self._writer.save_results(solution, result_name, **kwargs)
    
    # ===========================================================================
    # Mesh API
    # ===========================================================================
    
    @preinit_only
    def get_elements(self) -> list[Triangle]:
        """Returns the list of all mesh elements.

        Returns
        -------
        list of :class:`~lizzy._core.cvmesh.entities.Triangle`
            List of all Triangle elements in the mesh.
        """
        return self._mesh.triangles

    @preinit_only
    def get_element_by_idx(self, idx: int) -> Triangle:
        """Returns the mesh element at the given index.

        Parameters
        ----------
        idx : int
            Integer index of the element.

        Returns
        -------
        :class:`~lizzy.entities.Triangle`
            The element at the given index.
        """
        return self._mesh.triangles[idx]

    @preinit_only
    def get_nodes(self) -> list[Node]:
        """Returns the list of all mesh nodes.

        Returns
        -------
        list of :class:`~lizzy._core.cvmesh.entities.Node`
            List of all Node objects in the mesh.
        """
        return self._mesh.nodes

    @preinit_only
    def get_node_by_idx(self, idx: int) -> Node:
        """Returns the mesh node at the given index.

        Parameters
        ----------
        idx : int
            Integer index of the node.

        Returns
        -------
        :class:`~lizzy.entities.Node`
            The node at the given index.
        """
        return self._mesh.nodes[idx]
    
    # ===========================================================================
    # Simulation parameters
    # ===========================================================================

    @preinit_only
    def assign_simulation_parameters(self, **kwargs):
        r"""
        Assigns new values to one or more simulation parameters using keyword arguments.

        Parameters
        ----------
        **kwargs
            Keyword arguments corresponding to parameter names and their new values.
            Valid keywords are:

            - ``output_interval`` (float, optional): interval of simulation time between solution write-outs [s]. Default: -1 (write-out every numerical time step)
            - ``fill_tolerance`` (float, optional): tolerance on the fill factor to consider a CV as filled. Default: 0.01
            - ``end_step_when_sensor_triggered`` (bool, optional): if True, ends current solution step and creates a write-out when a sensor changes state. Default: False
        
        Examples
        --------
        >>> model.assign_simulation_parameters(output_interval=50)

        Raises
        ------
        AttributeError
            If any key in `kwargs` does not correspond to a known attribute.
        """
        self._simulation_parameters.assign(**kwargs)

    def print_simulation_parameters(self) -> None:
        """
        Print the currently assigned simulation parameters.
        """
        self._simulation_parameters.print_current()

    # ===========================================================================
    # Materials API
    # ===========================================================================

    @preinit_only
    def create_material(self, name : str, k_vals : tuple[float, float, float], porosity: float, thickness: float) -> PorousMaterial:
        """Create a new material that can then be selected and used in the model.

        Parameters
        ----------
        name : str
            Unique name of the new material.
        k_vals : tuple[float, float, float]
            Permeability values in the three principal directions (k1, k2, k3) [m²]. All values must be positive.
        porosity : float
            Volumetric porosity of the material (porosity = 1 - fibre volume fraction). Must be between 0 and 1 (exclusive).
        thickness : float
            Thickness of the material in the out-of-plane direction [m]. Must be positive.

        Returns
        -------
        :class:`~lizzy.materials.PorousMaterial`
            Reference to the created material.
        """
        new_material = self._material_manager.create_material(name, k_vals, porosity, thickness)
        return new_material
    
    @preinit_only
    def assign_material(self, material_selector:PorousMaterial | str, mesh_tag:str, rosette:Rosette = None) -> None:
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
        material, rosette = self._material_manager.assign_material(material_selector, mesh_tag, rosette)
        try:
            element_idxs = self._reader.mesh_data["physical_domains"][mesh_tag]
        except KeyError:
            raise KeyError(f"Domain tag '{mesh_tag}' not found in mesh physical domains. Check the name, or assign the material to an existing mesh tag.")
        self._mesh.update_elements_with_assigned_material(element_idxs, material, rosette)
    
    @preinit_only
    def create_resin(self, name : str, viscosity : float) -> Resin:
        """Create a new resin that can then be selected and used in the model.

        Parameters
        ----------
        name : str
            Unique name of the resin.
        viscosity : float
            Dynamic viscosity of the resin [Pa.s]
        
        Returns
        -------
        :class:`~lizzy.materials.Resin`
            Reference to the created resin.
        """
        new_resin = self._material_manager.create_resin(name, viscosity)
        return new_resin

    @preinit_only
    def assign_resin(self, resin_selector:Resin | str) -> None:
        """Assign an existing resin to the model.

        Parameters
        ----------
        resin_selector : Resin | str
            The resin object or name of the resin to assign. Must correspond to an existing resin created with :func:`~LizzyModel.create_resin`.
        """
        self._material_manager.assign_resin(resin_selector)

    @preinit_only
    def create_rosette(self, name:str, u:tuple[float, float, float]) -> Rosette:
        """Create a new orientation rosette that can then be used when assigning a material.

        Parameters
        ----------
        name : str
            Unique name of the new rosette.
        u : tuple[float, float, float]
            Direction vector defining the first principal direction of the rosette (k1 direction), expressed in global (x, y, z) coordinates. Does not need to be normalised.

        Returns
        -------
        :class:`~lizzy.materials.Rosette`
            Reference to the created rosette.
        """
        new_rosette = self._material_manager.create_rosette(name, u)
        return new_rosette
    
    # ===========================================================================
    # Gates API
    # ===========================================================================

    @preinit_only
    def create_pressure_inlet(self, name:str, initial_pressure_value:float) -> PressureInlet:
        """Creates a new inlet where a pressure boundary condition is applied.

        Parameters
        ----------
        name : str
            Name of the inlet.
        initial_pressure_value : float
            Initial pressure value at the inlet.

        Returns
        -------
        :class:`~lizzy.gates.PressureInlet`
            The created inlet.
        """
        new_inlet = self._gates_manager.create_pressure_inlet(name, initial_pressure_value)
        return new_inlet
    
    @preinit_only
    def create_flowrate_inlet(self, name:str, initial_flowrate_value:float) -> FlowRateInlet:
        """Creates a new inlet where a volumetric flow rate boundary condition is applied.

        Parameters
        ----------
        name : str
            Name of the inlet.
        initial_flowrate_value : float
            Initial volumetric flow rate value at the inlet.

        Returns
        -------
        :class:`~lizzy.gates.FlowRateInlet`
            The created inlet.
        """
        new_inlet = self._gates_manager.create_flowrate_inlet(name, initial_flowrate_value)
        return new_inlet

    @preinit_only
    def assign_inlet(self, inlet_selector:Inlet | str, boundary_tag:str) -> None:
        """Selects an inlet from created ones and assigns it to the indicated mesh boundary.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object to assign, or the name of an existing inlet.
        boundary_tag : str
            An existing mesh boundary tag where to assign the inlet.
        """
        self._gates_manager.assign_inlet(inlet_selector, boundary_tag)
    
    @preinit_only
    def create_vent(self, name:str, vacuum_pressure:float=0.0) -> Vent:
        """Creates a new vent where a vacuum pressure boundary condition is applied.

        Parameters
        ----------
        name : str
            Name of the vent.
        vacuum_pressure : float, optional
            Vacuum pressure value at the vent (default is 0.0).

        Returns
        -------
        :class:`~lizzy.gates.Vent`
            The created vent.
        """
        new_vent = self._gates_manager.create_vent(name, vacuum_pressure)
        return new_vent
    
    @preinit_only
    def assign_vent(self, vent_selector:Vent | str, boundary_tag:str) -> None:
        """Selects a vent from created ones and assigns it to the indicated mesh boundary.

        .. note::
            Currently only one vent can be assigned to the model. Attempting to assign a second vent will raise a :class:`~lizzy.exceptions.ConfigurationError`.

        Parameters
        ----------
        vent_selector : Vent | str
            Either the vent object to assign, or the name of an existing vent.
        boundary_tag : str
            An existing mesh boundary tag where to assign the vent.
        """
        self._gates_manager.assign_vent(vent_selector, boundary_tag)
    
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
        selected_inlet = self._gates_manager._fetch_inlet(inlet_name)
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
        ValueError
            If the `mode` is not one of the allowed values.
        """
        self._gates_manager.change_inlet_pressure(inlet_selector, pressure_value, mode)

    def open_inlet(self, inlet_selector:Inlet | str):
        """Sets the selected inlet state to `open`. When open, the inlet applies its p_value as a Dirichlet boundary condition. An inlet can be opened at any time during the simulation.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object reference, or the name of an existing inlet.
        """
        self._gates_manager.open_inlet(inlet_selector)

    def close_inlet(self, inlet_selector:Inlet | str):
        """Sets the selected inlet state to `closed`. When closed, the inlet acts as a Neumann natural boundary condition (no flux). An inlet can be closed at any time during the simulation. The stored p_value is preserved when the inlet is closed.

        Parameters
        ----------
        inlet_selector : Inlet | str
            Either the inlet object reference, or the name of an existing inlet.
        """
        self._gates_manager.close_inlet(inlet_selector)
    
    # ===========================================================================
    # Sensors API
    # ===========================================================================

    #TODO: get coords arg as tuple or np array, then ids as int or string
    @preinit_only
    def create_sensor(self, x:float, y:float, z:float) -> None:
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

    @postinit_only
    def print_sensor_readings(self):
        """Prints to the console the current readings of each sensor: time, pressure, fill factor and velocity.
        """
        self._sensor_manager.print_sensor_readings()

    @postinit_only
    def get_sensor_trigger_states(self) -> list[bool]:
        """Returns a list of sensor trigger states: True if the sensor has been triggered, False otherwise."""
        return self._sensor_manager.sensor_trigger_states
    
    def get_sensor_by_id(self, idx:int) -> Sensor:
        """Fetches a sensor by its index.

        Parameters
        ----------
        idx : int
            Index of the sensor to fetch. Sensors are indexed in the order they were created, starting from 0.

        Returns
        -------
        :class:`~lizzy.sensors.Sensor`
            The fetched sensor object.
        """
        return self._sensor_manager.get_sensor_by_id(idx)

    # ===========================================================================
    # Solver API
    # ===========================================================================

    def initialise_solver(self, solver_type:SolverType = SolverType.ITERATIVE_PETSC,
                         solver_tol:float = 1e-8, solver_max_iter:int = 1000,
                         solver_verbose:bool = False,
                         **solver_kwargs):
        """
        Initialize the solver for the filling simulation.

        Parameters
        ----------
        solver_type : SolverType
            Type of linear solver (DIRECT_DENSE, DIRECT_SPARSE, ITERATIVE_PETSC).
            Default is ITERATIVE_PETSC and will revert to DIRECT_SPARSE is PETSc is not installed.
        solver_tol : float
            Convergence tolerance for iterative solvers
        solver_max_iter : int
            Maximum iterations for iterative solvers
        solver_verbose : bool
            Print solver convergence information
        **solver_kwargs
            Additional solver-specific keyword arguments

        Raises
        ------
        ConfigurationError
            If required components (resin, materials, inlets, vents) are not properly assigned.
        """
        self._validate_configuration()

        self._solver = Solver(self._mesh, self._gates_manager, self._simulation_parameters,
                            self._material_manager, self._sensor_manager, solver_type,
                            solver_tol, solver_max_iter, solver_verbose, **solver_kwargs)

        self._state = State.POST_INIT

    def _validate_configuration(self):
        """Run all configuration checks before solver construction."""
        if not self._simulation_parameters.has_been_assigned:
            print(f"Warning: Simulation parameters were not assigned. Running with default values: output_interval={self._simulation_parameters.output_interval}")
        if not self._material_manager._resin_was_assigned:
            raise ConfigurationError("No resin assigned to the model. Create a resin using LizzyModel.create_resin and assign it using LizzyModel.assign_resin.")
        if len(self._gates_manager.assigned_inlets) == 0:
            raise ConfigurationError("No inlets assigned to the model. Create and assign at least one inlet before initialising the solver.")
        if len(self._gates_manager.assigned_vents) == 0:
            print("Warning: No vents assigned to the model. A default vent pressure of 0.0 Pa will be used.")
        self._gates_manager.assert_unique_boundary_assignments()
        self._mesh.assert_all_elements_have_material()

    @postinit_only
    def solve(self, log="on") -> Solution:
        """Advance the filling simulation from the current time until the part is filled.

        Parameters
        ----------
        log : str, optional
            Whether to print the progress of the solution, by default "on"

        Returns
        -------
        solution : :class:`~lizzy.datatypes.Solution`
            A Solution object storing the solution fields up to the time step reached
        """
        self._latest_solution = self._solver.solve(log=log, lightweight=self._lightweight)
        return self._latest_solution

    @postinit_only
    def solve_time_interval(self, time_interval:float, log="off") -> Solution:
        """Advance the filling simulation from the current time for the specified time interval.

        Parameters
        ----------
        time_interval : float
            The time period to advance the simulation for.
        log : str, optional
            Whether to print the progress of the solution, by default "off"

        Returns
        -------
        solution : :class:`~lizzy.datatypes.Solution`
            A Solution object storing the solution fields up to the time step reached.
        """
        self._latest_solution = self._solver.solve_time_interval(time_interval, log=log, lightweight=self._lightweight)
        return self._latest_solution
    
    @postinit_only
    def initialise_new_solution(self):
        """
        Initialises a new solution, resetting all simulation variables. The part will be emptied and initial boundary conditions restored. This method can be called to reset a simulation and run a new one, without resetting the model.
        """
        self._solver.initialise_new_solution()