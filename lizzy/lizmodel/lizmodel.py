#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from typing import Dict
from lizzy.IO.IO import Reader, Writer
from lizzy.cvmesh.cvmesh import Mesh
from lizzy.materials import MaterialManager, PorousMaterial, Rosette
from lizzy.sensors.sensmanager import SensorManager
from lizzy.simparams import SimulationParameters
from lizzy.bcond.bcond import BCManager
from lizzy.solver.solver import Solver, SolverType

class LizzyModel:
    def __init__(self):
        self._reader = None
        self._writer = None
        self._mesh = None
        self._solver = None
        self._simulation_parameters = SimulationParameters()
        self._material_manager = MaterialManager()
        self._bc_manager = BCManager()
        self._sensor_manager = SensorManager()
        self._lightweight = False

    @property
    def lightweight(self):
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

    @property
    def current_time(self) -> float:
        return self._solver.current_time

    def assign_simulation_parameters(self, **kwargs):
        self._simulation_parameters.assign(**kwargs)

    def read_mesh_file(self, mesh_file_path:str):
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

    def create_sensor(self, x:float, y:float, z:float, idx=None):
        self._sensor_manager.add_sensor(x, y, z, idx)

    def print_sensor_readings(self):
        self._sensor_manager.print_sensor_readings()
    
    def get_sensor_trigger_states(self):
        return self._sensor_manager.sensor_trigger_states
    
    def get_sensor_by_id(self, idx):
        return self._sensor_manager.get_sensor_by_id(idx)

    def initialise_solver(self, solver_type:SolverType = SolverType.DIRECT_DENSE):
        self._solver = Solver(self._mesh, self._bc_manager, self._simulation_parameters, self._material_manager, self._sensor_manager, solver_type)

    def solve(self):
        solution = self._solver.solve()
        return solution

    def solve_step(self, step_period:float):
        solution = self._solver.solve_step(step_period, log="off", lightweight=self._lightweight)
        return solution
    
    def initialise_new_solution(self):
        self._solver.initialise_new_solution()
    



