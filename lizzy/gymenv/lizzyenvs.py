import lizzy as liz
import gymnasium as gym

# class LizzyEnv(gym.Env):
#     def __init__(self):
#         super().__init__()
#         self.lizzy_model = liz.LizzyModel()
#         self.solver = None
#         self.step_duration = 0
#         self.materials = []
#         self.sensors = []
#         self.inlets = []
#         self.bc_manager = None
#         self.interactive = False
#         self.interactive_hold_time = 0.5
#         self.prefill = -1
#         self.solution = None
#
#     def read_mesh_file(self, path:str):
#         self.lizzy_model.read_mesh_file(path)
#
#     # def add_sensor(self , position:tuple):
#     #     liz.SensorManager.add_sensor(position[0], position[1], position[2])
#     #     self.sensors.append(liz.SensorManager.sensors[-1])
#
#     def assign_simulation_parameters(self, **kwargs):
#         self.lizzy_model.assign_simulation_parameters(**kwargs)
#
#     def create_porous_material(self, k1: float, k2: float, k3: float, porosity: float, thickness: float, name:str= None):
#         new_material = self.lizzy_model.create_porous_material(k1, k2, k3, porosity, thickness, name)
#         return new_material
#
#     def assign_material(self, porous_material, material_tag:str, rosette = None):
#         self.lizzy_model.assign_material(porous_material, material_tag, rosette)
#
#     def create_inlet(self, initial_pressure_value:float, name:str = None):
#         new_inlet = self.lizzy_model.create_inlet(initial_pressure_value, name)
#         return new_inlet
#
#     def assign_inlet(self, inlet, boundary_tag:str):
#         self.lizzy_model.assign_inlet(inlet, boundary_tag)
#
#     def initialise_solver(self, solver_type):
#         self.lizzy_model.initialise_solver(solver_type)
#
#     def solve(self):
#         solution = self.lizzy_model.solve()
#         return solution

class LizzyEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.lizzy_model = liz.LizzyModel()

    def __getattr__(self, name):
        return getattr(self.lizzy_model, name)
