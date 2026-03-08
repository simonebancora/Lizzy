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