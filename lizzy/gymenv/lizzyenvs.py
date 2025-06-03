#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import lizzy as liz
import gymnasium as gym
from lizzy.lizmodel import LizzyModel

class LizzyEnv(gym.Env):
    def __init__(self, lizzy_model:LizzyModel = None):
        super().__init__()
        if lizzy_model is not None:
            self.lizzy_model = lizzy_model
        else:
            self.lizzy_model = LizzyModel()

    def __getattr__(self, name):
        return getattr(self.lizzy_model, name)
