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
        self.target_velocity = 0
        self.p0 = 0
        self.discrete_delta_p = 1000
        self.action_space_type = action_space_type

        self.observation_space = gym.spaces.Dict(
            {
                "velocity": gym.spaces.Box(0, np.inf, shape=(1,), dtype=float),
                "target_velocity": gym.spaces.Box(0, np.inf, shape=(1,), dtype=float),
                "current_inlet_p" : gym.spaces.Box(0, np.inf, shape=(1,), dtype=float),
                "current_fill_percent" : gym.spaces.Box(0, 1, shape=(1,), dtype=float),
            }
        )

        match action_space_type:
            case "discrete":
                self.action_space = gym.spaces.Discrete(3)
                self.actions_map = {0 : -1,
                            1 : 0,
                            2 : 1}
            case "continuous":
                self.action_space = gym.spaces.Box(-1, 1, shape=(1,), dtype=float)
            case _:
                pass


    def set_target_velocity(self, value):
        self.target_velocity = value
    
    def set_initial_pressure(self, value):
        self.p0 = value
    
    def set_step_duration(self, value):
        self.step_duration = value
    
    def set_discrete_delta_p(self, value):
        self.discrete_delta_p = value


    def get_obs(self):

        v = self.sensors[0].vvals[-1][0]
        p = self.sensors[0].pvals[-1]
        fill_percent = 1.0 - self.solver.n_empty_cvs/self.solver.N_nodes

        return {"velocity": v, "target_velocity": self.target_velocity, "current_inlet_p": p, "current_fill_percent" : fill_percent}
    
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
        if self.inlets[0].p_value <= 0:
            truncated = True
        if not truncated or terminated:
            self.solution = self.solver.solve_step(self.step_duration, log="off")
            print("solving one step")
        if self.solver.n_empty_cvs <= 0:
            terminated = True
        observations = self.get_obs()
        reward = self.calculate_reward(observations)
        info = {}
        return observations, reward, terminated, truncated, info
    
    def reset(self, seed=None, options=None):
        if self.interactive:
            self.plot_episode(self.interactive_hold_time)
        self.inlets[0].p_value = self.p0
        self.sensors[0].reset()
        self.solver.initialise_new_solution()
        if self.prefill > 0:
            self.solver.solve_step(self.prefill)
            
        observations = self.get_obs()
        info = {}
        return observations, info
    
    def calculate_reward(self, observations):
        v_current = observations["velocity"]
        v_target = self.target_velocity
        err = np.abs(v_current - v_target)/v_target
        return 1 - 10*err
    
    def plot_episode(self, hold=5):
        v = self.sensors[0].vvals
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.set_title("Pressure")
        ax2.set_title("Velocity")
        # plt.tight_layout()
        ax1.plot(self.sensors[0].tvals, self.sensors[0].pvals)
        ax2.plot(self.sensors[0].tvals, [val[0] for val in v])
        ax2.plot(self.sensors[0].tvals, [self.target_velocity]*len(self.sensors[0].tvals))
        plt.show(block=True)
        if hold > 0:
            plt.pause(hold)
            plt.close()
