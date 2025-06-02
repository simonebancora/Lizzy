import lizzy as liz
import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt


class LizzyEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.solver = None
        self.step_duration = 0
        self.mesh = None
        self.materials = []
        self.sensors = []
        self.inlets = []
        self.bc_manager = liz.BCManager()
        self.interactive = False
        self.interactive_hold_time = 0.5
        self.prefill = -1
        self.solution = None

    
    def read_mesh(self, path:str):
        mesh_reader = liz.Reader(path)
        self.mesh = liz.Mesh(mesh_reader)
    
    def save_episode_result(self):
        # Create a write-out object and save results
        writer = liz.Writer(self.mesh)
        writer.save_results(self.solution, "episode_result")
    
    def add_sensor(self , position:tuple):
        liz.SensorManager.add_sensor(position[0], position[1], position[2])
        self.sensors.append(liz.SensorManager.sensors[-1])
    
    def assign_simulation_parameters(self, **kwargs):
        liz.SimulationParameters.assign(**kwargs)
    
    def assign_lizzy_mesh(self, mesh:liz.Mesh):
        self.mesh = mesh
    
    def create_material(self, k1:float, k2:float, k3:float,  porosity:float, thickness:float):
        new_material = liz.PorousMaterial(k1, k2, k3, porosity, thickness)
        self.materials.append(new_material)
        return new_material
    
    def assign_material(self, tag:str, material:liz.PorousMaterial):
        liz.MaterialManager.add_material(tag, material)
    
    def create_inlet(self, p0:float):
        new_inlet = liz.Inlet("none", p0)
        self.inlets.append(new_inlet)
        return new_inlet
    
    def assign_inlet(self, tag:str, inlet:liz.Inlet):
        inlet.physical_tag = tag
        self.bc_manager.add_inlet(inlet)
    
    def initialise_solver(self):
        self.solver = liz.Solver(self.mesh, self.bc_manager, liz.SolverType.DIRECT_SPARSE)
    
    def solve_until_filled(self):
        self.solution = self.solver.solve(log="on")
        return self.solution



