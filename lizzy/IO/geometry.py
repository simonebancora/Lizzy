#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np

# Extract lines: they will be REPEATED
def extract_lines(nodes_conn):
    """
    Extract lines connectivity from a nodes connectivity table.

    Parameters
    ----------
    nodes_conn: list
        The nodes connectivity table of the mesh

    Returns
    -------
    lines_conn : list
        The lines connectivity table
    """
    lines_conn = []
    n_geom = len(nodes_conn[0])
    for e in nodes_conn:
        candidate_lines_conns = []
        for i in range(n_geom-1):
            candidate_lines_conns.append([e[i], e[i+1]])
        candidate_lines_conns.append([e[i+1], e[0]])
        for line_conn in candidate_lines_conns:
            line_test_1 = [line_conn[0], line_conn[1]]
            line_test_2 = [line_conn[1], line_conn[0]]
            # if normals give problems, might be necessary to not get repeated lines
            if line_test_1 not in lines_conn and line_test_2 not in lines_conn:
                lines_conn.append(line_conn)
    return lines_conn


def extract_unique_nodes(node_ids_list):
    """
    Return unique nodes from an array of nodes
    """
    repeated_nodes = np.concatenate(node_ids_list, axis=None)
    non_repeated_nodes = np.unique(repeated_nodes)
    return non_repeated_nodes

