#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
from dataclasses import dataclass
import textwrap

@dataclass
class SimulationParameters:
    """Data class that stores several parameters used by the simulation.

    Attributes
    ----------
    output_interval : float
        Interval of simulation time between solution write-outs [s]. Default: -1 (write-out every numerical time step)
    fill_tolerance : float
        Tolerance on the fill factor to consider a CV as filled. Default: 0.01
    end_step_when_sensor_triggered : bool
        If True, ends current solution step and creates a write-out when a sensor changes state. Default: False


    """
    output_interval: float = -1
    fill_tolerance: float = 0.01
    has_been_assigned : bool = False
    end_step_when_sensor_triggered : bool = False
    generate_fill_image :bool = False
    fill_image_resolution : int = 250
    display_fill : bool = False

    def print_current(self):
        """Prints the currently assigned simulation parameters to the console."""
        params = textwrap.dedent(rf"""
        Currently assigned simulation parameters:
        - "output_interval": {self.output_interval} [s],
        - "fill_tolerance": {self.fill_tolerance},
        - "end_step_when_sensor_triggered": {self.end_step_when_sensor_triggered}
        """)
        print(params)


    def assign(self, **kwargs):
        r"""
        Assigns new values to one or more simulation parameters using keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments corresponding to parameter names and their new values.
            Each key must be a valid attribute of the `SimulationParameters` class, otherwise, an `AttributeError` is raised. Valid parameters are:
        
            - ``output_interval``: interval of simulation time between solution write-outs [s]. Default: -1 (write-out every numerical time step)
            - ``fill_tolerance``: tolerance on the fill factor to consider a CV as filled. Default: 0.01
            - ``end_step_when_sensor_triggered``: if True, ends current solution step and creates a write-out when a sensor changes state. Default: False

        Raises
        ------
        AttributeError
            If any key in `kwargs` does not correspond to a known attribute.
        """
        # TODO: this probably breaks
        _ALIASES = {"wo_delta_time": "output_interval"}
        self.has_been_assigned = True
        for key, value in kwargs.items():
            resolved_key = _ALIASES.get(key, key)
            if hasattr(self, resolved_key):
                setattr(self, resolved_key, value)
            else:
                raise AttributeError(f"'{self.__class__.__name__}' Error: unknown attribute '{key}'")
