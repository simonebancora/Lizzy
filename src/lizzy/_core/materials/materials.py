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
    k1: float
        Principal permeability in local direction e1.
    k2: float
        Principal permeability in local direction e2.
    k3: float
        Principal permeability in local direction e3.
    porosity: float
        Porosity of the material (between 0 and 1).
    thickness: float
        Thickness of the material in the out-of-plane direction.
    name: str
        Name/label of the material.
    """
    def __init__(self, k1:float, k2:float, k3:float,  porosity:float, thickness:float, name:str = "unnamed_material"):
        self.k_diag = np.array([[k1, 0, 0],[0, k2, 0],[0, 0, k3]])
        self.porosity = porosity
        self.thickness = thickness
        self.name = name
        self.is_isotropic = np.allclose([k1, k2, k3], k1, atol=1e-14, rtol=0)
        self.assigned = False

