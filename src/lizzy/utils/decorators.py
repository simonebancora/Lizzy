#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy.model import LizzyModel

from functools import wraps
from enum import Enum

from lizzy.exceptions import StateError


class State(Enum):
    PRE_INIT    = 0
    POST_INIT   = 1

def preinit_only(method):
    @wraps(method)
    def wrapper(self:LizzyModel, *args, **kwargs):
        if self._state != State.PRE_INIT:
            raise StateError(f"Method '{method.__name__}' must be called before initialise_solver().")
        return method(self, *args, **kwargs)
    return wrapper

def postinit_only(method):
    @wraps(method)
    def wrapper(self:LizzyModel, *args, **kwargs):
        if self._state != State.POST_INIT:
            raise StateError(f"Method '{method.__name__}' must be called after initialise_solver().")
        return method(self, *args, **kwargs)
    return wrapper