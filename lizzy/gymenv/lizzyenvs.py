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
        solution = self.solver.solve(log="on")
        return solution

class LizzyVelocityEnv(LizzyEnv):
    def __init__(self, action_space_type="discrete"):
        super().__init__()
        self.target_velocity = 0.0
        self.target_tolerance = 0.1
        self.p0 = 0
        self.discrete_delta_p = 1000
        self.current_normalised_v = 0
        self.current_p = 0
        self.previous_normalised_v = 0
        self.action_space_type = action_space_type
        self.observations = None
        self.velocity_err_weight = 10
        self.max_penalty = -100
        self.target_velocity_range = (0, 0)
        self.current_velocity_error = 0
        self.previous_velocity_error = 0

        self.observation_space = gym.spaces.Dict(
            {
                "current_velocity_error": gym.spaces.Box(0, np.inf, shape=(1,), dtype=float),
                "previous_velocity_error": gym.spaces.Box(0, np.inf, shape=(1,), dtype=float),
                "current_inlet_p" : gym.spaces.Box(0, np.inf, shape=(1,), dtype=float),
                "current_fill_percent" : gym.spaces.Box(0, 1, shape=(1,), dtype=float),
            }
        )

        match self.action_space_type:
            case "discrete":
                self.action_space = gym.spaces.Discrete(3)
                self.actions_map = {0 : -1,
                            1 : 0,
                            2 : 1}
            case "continuous":
                self.action_space = gym.spaces.Box(-1, 1, shape=(1,), dtype=float)
            case _:
                pass

    def set_target_velocity_range(self, min_val, max_val, tol):
        self.target_velocity_range = (min_val, max_val)
        self.target_tolerance = tol

    def set_initial_pressure(self, value):
        self.p0 = value
    
    def set_step_duration(self, value):
        self.step_duration = value
    
    def set_discrete_delta_p(self, value):
        self.discrete_delta_p = value

    def get_obs(self):
        self.previous_normalised_v = self.current_normalised_v
        self.current_normalised_v = self.sensors[0].vvals[-1][0]/self.target_velocity
        self.current_velocity_error = np.abs(self.current_normalised_v - 1.0)
        self.previous_velocity_error = np.abs(self.previous_normalised_v - 1.0)
        self.current_p = self.sensors[0].pvals[-1]
        fill_percent = 1.0 - self.solver.n_empty_cvs/self.solver.N_nodes
        self.observations = {"current_velocity_error": self.current_velocity_error, "previous_velocity_error": self.previous_velocity_error, "current_inlet_p": self.current_p, "current_fill_percent" : fill_percent}
        return self.observations
    
    def step(self, action):
        truncated = False
        terminated = False
        match self.action_space_type:
            case "discrete":
                new_p_increment = self.actions_map[int(action)]*self.discrete_delta_p
            case "continuous":
                new_p_increment = action[0] * self.discrete_delta_p
            case _:
                NameError
        self.inlets[0].p_value += new_p_increment
        if self.inlets[0].p_value <= 1000:
            truncated = True
        if not truncated or terminated:
            self.solution = self.solver.solve_step(self.step_duration, log="off")
        if self.solver.n_empty_cvs <= 0:
            terminated = True
        self.observations = self.get_obs()
        reward = self.calculate_reward(self.observations)
        if truncated:
            reward = self.max_penalty
        info = {}
        return self.observations, reward, terminated, truncated, info
    
    def reset(self, seed=None, options=None):
        if self.interactive:
            self.plot_episode(self.interactive_hold_time)
        self.inlets[0].p_value = self.p0
        self.current_p = self.p0
        self.target_velocity = np.random.uniform(self.target_velocity_range[0], self.target_velocity_range[1])
        self.sensors[0].reset()
        self.solver.initialise_new_solution()
        self.current_normalised_v = 1.0
        self.previous_normalised_v = 1.0
        if self.prefill > 0:
            self.solver.solve_step(self.prefill)
        self.observations = self.get_obs()
        info = {}
        return self.observations, info
    
    def calculate_reward(self, observations):
        if self.current_velocity_error <= self.target_tolerance:
            reward = 100
        else:
            reward = 10*(self.previous_velocity_error - self.current_velocity_error)
        reward = np.maximum(reward, self.max_penalty)
        return reward
    
    def plot_episode(self, hold:float=5):
        v = self.sensors[0].vvals
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax2.set_title("Pressure")
        ax1.set_title("Velocity")
        ax1.set_ylim([0, self.target_velocity*4/3])
        plt.tight_layout()
        ax2.plot(self.sensors[0].tvals[1:], self.sensors[0].pvals[1:])
        ax1.plot(self.sensors[0].tvals[1:], [val[0] for val in v][1:])
        ax1.plot(self.sensors[0].tvals[1:], [self.target_velocity]*(len(self.sensors[0].tvals)-1))
        plt.show(block=False)
        if hold > 0:
            plt.pause(hold)
            plt.close()
