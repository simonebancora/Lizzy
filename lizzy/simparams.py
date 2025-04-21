#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

class ProcessParameters:
    """
    Defines some global parameters for the simulation. Attribute values can be assigned as kwargs of the ``assign`` method.

    Attributes
    ----------
    mu: float
        Dynamic viscosity of the fluid
    wo_delta_time: float
        Time intervals at which results will be saved
    write_all_steps: bool
        If True, all time steps will be saved and "wo_delta_time" will be ignored (default: False)
    """
    def __new__(cls, *args, **kwargs):
        raise TypeError(f"{cls.__name__} is a singleton and must not be instantiated.")
    mu: float = 0.1
    wo_delta_time: float = -1
    fill_tolerance: float = 0.00
    has_been_assigned = False

    @classmethod
    def assign(cls, **kwargs):
        cls.has_been_assigned = True
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                raise AttributeError(f"'{cls.__name__}' Error: unknown attribute '{key}'")
