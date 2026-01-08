#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from enum import Enum, auto

class LogLevel(Enum):
    NONE = auto()
    PREPROCESS = auto()
    SOLVER = auto()
    ALL = auto()

class Stage(Enum):
    PREPROCESS = auto()
    SOLVER = auto()


class Logger:
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} cannot be instantiated.")
    log_level = LogLevel.ALL
    current_stage = Stage.PREPROCESS

    @classmethod
    def log(cls, message:str):
        match cls.log_level:
            case LogLevel.NONE:
                return
            case LogLevel.PREPROCESS if cls.current_stage == Stage.PREPROCESS:
                print(f"\n{message}")
            case LogLevel.SOLVER if cls.current_stage == Stage.SOLVER:
                print("\r{} TEST".format(message), end='')
            case LogLevel.ALL:
                print(f"\n{message}")
            case _:
                return
