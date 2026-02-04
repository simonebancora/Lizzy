#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

class PorousMaterial:
    """
    Porous material defined by principal permeability values, porosity and thickness.

    Parameters
    ----------
    name: str
        Name/label of the material.
    k_vals: tuple[float, float, float]
        Permeability values in principal directions.
    porosity: float
        Porosity of the material (between 0 and 1).
    thickness: float
        Thickness of the material in the out-of-plane direction.
    """
    def __init__(self, name:str, k_vals : tuple[float, float, float], porosity:float, thickness:float):
        self.is_isotropic = np.allclose([k_vals[0], k_vals[1], k_vals[2]], k_vals[0], atol=1e-14, rtol=0)
        self.k_princ = np.diag(k_vals)
        self.porosity = porosity
        self.thickness = thickness
        self.name = name
        self.assigned = False


class Resin:
    __slots__ = ("name", "mu")
    """Resin defined by dynamic viscosity (constant).

    Parameters
    ----------
    name: str
        Name of the resin.
    mu: float
        Dynamic viscosity of the resin [Pa.s]
    """
    def __init__(self, name:str, mu:float):
        self.name = name
        self.mu = mu