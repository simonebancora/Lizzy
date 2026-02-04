#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.io import Reader
    from lizzy._core.materials import MaterialManager, Rosette, PorousMaterial
    from lizzy._core.cvmesh.entities import Node, Line, Triangle, CV

import numpy as np
from .construction import MeshBuilder, MeshView
from .collections import nodes, lines, elements


class Mesh:
    r"""
    A class representing a FE/CV mesh.

    The Mesh class provides methods for creating and manipulating a mesh. Takes a mesh_data dictionary coming from the mesh reader, and creates objects for all entities (nodes, elements, lines). Also creates the control volumes (CVs).

    Parameters
    ----------
    mesh_reader : IO.Reader
        Dictionary containing mesh data, returned by IO.Reader

    """
    def __init__(self, mesh_reader:Reader):
        self.mesh_view:MeshView = None
        self.mesh_data = mesh_reader.mesh_data
        self.nodes : list[Node] = nodes([])
        self.lines : list[Line] = lines([])
        self.triangles : list[Triangle] = elements([])
        self.tetras = elements([])
        self.CVs :list[CV] = []

        # Init methods:
        self.mb = MeshBuilder()
        self.nodes, self.lines, self.triangles, self.CVs, self.mesh_view = self.mb.build_mesh(self.mesh_data)

    def empty_cvs(self):
        for cv in self.CVs:
            cv.fill = 0
