#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from gymnasium import Env
from lizzy.lizmodel.lizmodel import LizzyModel
from abc import abstractmethod

class LizzyEnv(LizzyModel, Env):
    """Environment base class for constructing custom Gymnasium environments that include Lizzy as simulator. The class inherits from LizzyModel, so the environment can be used just like the model for defining and controlling simulations. It also adds some additional APIs specific to Reinforcement Learning workflow."""
    def __init__(self):
        LizzyModel.__init__(self)
        Env.__init__(self)
        self._step_duration:float       = 1
        self._prefill:float             = -1
        self._latest_solution:any       = None
        self._verbose:bool              = False
        self._episode_counter:int       = 0
        self._step_counter:int          = 0
        self._observation_space:any     = None
        self._action_space:any          = None

    @property
    def step_duration(self):
        """The duration in seconds of a step taken by the agent. This sets how much time the simulation will advance during the step() method of the environment. It has no relation with the time step calculation of the solver (which is determined internally and plays no role in the training step duration)."""
        return self._step_duration

    @step_duration.setter
    def step_duration(self, value):
        self._step_duration = value
    
    @property
    def prefill(self):
        """The time in seconds the model will be infused using initial conditions before the agent begins taking actions in steps. The prefill is executed at each environment reset. Setting this parameter to any value > 0 will trigger the prefill. Default value is -1 (no prefill)."""
        return self._prefill

    @prefill.setter
    def prefill(self, value:float):
        self._prefill = value
    
    @property
    def episode_counter(self):
        """A counter for the episodes executed by the environment. This counter advances at the start of each new episode and is never reset during environment runtime"""
        return self._episode_counter
    
    @episode_counter.setter
    def episode_counter(self, value):
        self._episode_counter = value
    
    @property
    def step_counter(self):
        """A counter for the steps taken by the agent within an episode. The prefill step does not contribute to the counter, only steps taken by the agent. This parameter is set to 0 at each reset of the environment."""
        return self._step_counter
    
    @step_counter.setter
    def step_counter(self, value):
        self._step_counter = value
    

    
    def set_verbose(self, value:bool=True):
        """Sets the verbose flag for the LizzyEnv.log() method. If true, arguments passed to the log() method are printed to the console."""
        self._verbose = value
    
    @property
    def observation_space(self):
        """The observation space defined for this Gymnasium environment"""
        return self._observation_space
    
    @observation_space.setter
    def observation_space(self, value):
        self._observation_space = value
    
    @property
    def action_space(self):
        """The action space defined for this Gymnasium environment"""
        return self._action_space

    @action_space.setter
    def action_space(self, value):
        self._action_space = value
    
    
    @abstractmethod
    def step(self, action):
        self.log(f"\nSTEP :\n")
        self.log(f"action : {action}" )
        self.step_counter += 1
    
    @abstractmethod
    def reset(self,seed=None, options=None):
        super().reset(seed=seed)
        self.step_counter = 0
        self.episode_counter += 1
        self.log(f"\n-----------\nNEW EPISODE : {self.episode_counter}\n-----------\n")
    
    def log(self, message:str):
        if self._verbose:
            print(message)


