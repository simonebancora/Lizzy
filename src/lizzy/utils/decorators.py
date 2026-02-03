from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy.model import LizzyModel

import sys
from functools import wraps
from enum import Enum


class State(Enum):
    PRE_INIT    = 0
    POST_INIT   = 1

def preinit_only(method):
    @wraps(method)
    def wrapper(self:LizzyModel, *args, **kwargs):
        if self._state != State.PRE_INIT:
            print(f"ERROR: Method '{method.__name__}' must be called before `initialise_solver()`.")
            sys.exit(1)
        return method(self, *args, **kwargs)
    return wrapper

def postinit_only(method):
    @wraps(method)
    def wrapper(self:LizzyModel, *args, **kwargs):
        if self._state != State.POST_INIT:
            print(f"ERROR: Method '{method.__name__}' must be called after initialise_solver().")
            sys.exit(1)
        return method(self, *args, **kwargs)
    return wrapper