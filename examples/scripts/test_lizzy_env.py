from lizzy.gymenv.lizzyenvs import LizzyVelocityEnv
from gymnasium.wrappers import FlattenObservation
import stable_baselines3 as sb3
import numpy as np

env = LizzyVelocityEnv()

env.read_mesh("../meshes/Rect1M_R1.msh")

env.assign_simulation_parameters(mu=0.1, wo_delta_time=np.inf, fill_tolerance=0.05)

mat = env.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0)
env.assign_material("domain", mat)

inlet = env.create_inlet(100000)
env.assign_inlet("left_edge", inlet)

sensor_position = (0.0, 0.25, 0)
env.add_sensor(sensor_position)

env.initialise_solver()



env.set_step_duration(10)
env.set_target_velocity(0.0003)
env.set_initial_pressure(100000)
env.set_discrete_delta_p(10000)


env_flattened = FlattenObservation(env)

model = sb3.PPO("MlpPolicy", env_flattened)


n_episodes = 10





for i in range(n_episodes):
    observations, info = env_flattened.reset()
    # prefill a little
    env.solver.solve_step(40)
    env.sensors[0].reset()
    terminated = False
    truncated = False
    episode_return = 0
    actions_taken = []
    while not terminated or truncated:
        action, _ = model.predict(observations)
        next_observations, reward, terminated, truncated, info = env_flattened.step(action)
        actions_taken.append(action)
        episode_return += reward
    env.plot_episode(5)
        
    