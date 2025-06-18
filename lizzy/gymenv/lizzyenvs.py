#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from gymnasium import Env
from lizzy.lizmodel.lizmodel import LizzyModel
from abc import abstractmethod

class LizzyEnv(LizzyModel, Env):
    def __init__(self):
        LizzyModel.__init__(self)
        Env.__init__(self)
        self._step_duration:float       = 1
        self._prefill:float             = -1
        self._latest_solution           = None
        self._verbose : bool            = False
        self._episode_counter : int     = 0
        self._step_counter : int        = 0
        self._observation_space : any   = None
        self._action_space : any        = None

    # ATTRIBUTES
    @property
    def step_duration(self):
        return self._step_duration

    @step_duration.setter
    def step_duration(self, value):
        self._step_duration = value
    
    @property
    def prefill(self):
        return self._prefill

    @prefill.setter
    def prefill(self, value:float):
        self._prefill = value
    
    @property
    def episode_counter(self):
        return self._episode_counter
    
    @episode_counter.setter
    def episode_counter(self, value):
        self._episode_counter = value
    
    @property
    def step_counter(self):
        return self._step_counter
    
    @step_counter.setter
    def step_counter(self, value):
        self._step_counter = value
    
    @property
    def latest_solution(self):
        return self._latest_solution
    
    def set_verbose(self, value:bool=True):
        self._verbose = value
    
    @property
    def current_solution(self):
        return self._current_solution
    
    @property
    def observation_space(self):
        return self._observation_space
    
    @observation_space.setter
    def observation_space(self, value):
        self._observation_space = value
    
    @property
    def action_space(self):
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
