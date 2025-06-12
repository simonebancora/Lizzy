#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from gymnasium import Env
from lizzy.lizmodel.lizmodel import LizzyModel

class LizzyEnv(LizzyModel, Env):
    def __init__(self):
        LizzyModel.__init__(self)
        Env.__init__(self)
        self._step_duration:float = 1
        self._prefill:float = -1
        self._current_solution = None
        self._verbose : bool = False

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
    
    def set_verbose(self, value:bool=True):
        self._verbose = value
    
    @property
    def current_solution(self):
        return self._current_solution

    def get_obs(self):
        raise NotImplementedError
    
    def step(self, action):
        raise NotImplementedError
    
    def reset(self,seed=None, options=None):
        super().reset(seed=seed)
    
    def log(self, message:str):
        if self._verbose:
            print(message)
