#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

class Rosette:
    """Rosette object to define the orientation of the material in the mesh elements. The rosette is always projected on each element along the element normal direction. It is initialised by defining the e1 axis of the rosette (k1 direction) as two points in 3D space: e1 = p1 - p0

    Parameters
    ----------
    name : str
        The unique name of the rosette.
    p1 : tuple[float, float, float]
        The vector defining the first axis of the rosette (k1 direction).
    """
    def __init__(self, name:str, u=(1.0,0,0)):
        self.name = name
        self.u = np.array(u)

    #TODO: this needs reviewing
    def project_along_normal(self, normal):
        u_normal = np.dot(self.u, normal) * normal
        u_project = self.u - u_normal
        u_project = u_project / np.linalg.norm(u_project)
        v_project = np.cross(u_project, normal)
        v_project = v_project / np.linalg.norm(v_project)
        return u_project, v_project, normal
