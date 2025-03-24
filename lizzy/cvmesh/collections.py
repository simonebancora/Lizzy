#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

# Extends List to create a few special lists containing additional attributes: nodes, lines, elements

class nodes(list):
    """
    List of all Nodes in the mesh. Extends List class with additional attributes.
    Created when initialising Mesh.

    Attributes
    ----------
    XYZ : ndarray
        Array of all node coordinates, in shape (n_nodes, 3)
    N : int
        Number of nodes in the mesh
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args[0])
        self.XYZ : np.ndarray = None
        self.N : int = 0

class elements(list):
    """
    List of all Elements in the mesh. Extends List class with additional attributes.
    Created when initialising Mesh.

    Attributes
    ----------
    N : int
        Number of elements in the mesh
    nodes_conn_table : ndarray
        Nodal connectivity table of elements
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args[0])
        self.N : int = 0
        self.nodes_conn_table : np.ndarray = None

class lines(list):
    """
    List of all Lines in the mesh. Extends List class with additional attributes.
    Created when initialising Mesh.

    Attributes
    ----------
    N : int
        Number of lines in the mesh
    nodes_conn_table : ndarray
        Nodal connectivity table of lines
    """
    def __init__(self, *args, **kwargs):
        super().__init__(args[0])
        self.N : int = 0
        self.nodes_conn_table : np.ndarray = None
        self.T_nodes_inlet : np.ndarray = None
        self.T_nodes_vent : np.ndarray = None