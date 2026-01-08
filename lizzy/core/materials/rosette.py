#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

class Rosette:
    """Rosette object to define the orientation of the material in the mesh elements. The rosette is always projected on each element along the element normal direction. Can be initialised by passing one vector, or 2 points.
    """
    def __init__(self, u=(1.0,1.0,1.0), p0=(0.0,0.0,0.0)):
        u = np.array(u)
        self.p0 = np.array(p0)
        self.u = p0 - u

    def project_along_normal(self, normal):
        u_normal = np.dot(self.u, normal) * normal
        u_project = self.u - u_normal
        u_project = u_project / np.linalg.norm(u_project)
        v_project = np.cross(u_project, normal)
        v_project = v_project / np.linalg.norm(v_project)
        return u_project, v_project, normal
