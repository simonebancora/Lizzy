#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import logging
import os
from pathlib import Path
from enum import Enum, auto
import numpy as np
import meshio
import textwrap

from lizzy.exceptions import MeshError

logger = logging.getLogger("lizzy.io")

def extract_unique_nodes(node_ids_list):
    """
    Return unique nodes from an array of nodes
    """
    repeated_nodes = np.concatenate(node_ids_list, axis=None)
    non_repeated_nodes = np.unique(repeated_nodes)
    return non_repeated_nodes

def populate_mesh_data(all_nodes_coords,
                    nodes_conn,
                    *,
                    physical_lines_conn=None,
                    physical_domains=None,
                    physical_lines=None,
                    physical_nodes_ids=None,
                    physical_domain_names=None,
                    physical_line_names=None) -> dict:
    mesh_data = {
        'all_nodes_coords'      : all_nodes_coords,
        'nodes_conn'            : nodes_conn,
        'physical_lines_conn'   : {} if physical_lines_conn is None else physical_lines_conn,
        'physical_domains'      : {} if physical_domains is None else physical_domains,
        'physical_lines'        : {} if physical_lines is None else physical_lines,
        'physical_nodes'        : {} if physical_nodes_ids is None else physical_nodes_ids,
        'physical_domain_names' : [] if physical_domain_names is None else physical_domain_names,
        'physical_line_names'   : [] if physical_line_names is None else physical_line_names,
        }

    return mesh_data

class Format(Enum):
    MSH = auto()
    INP = auto()
    STL = auto()

class Reader:
    """Handles reading and parsing mesh files, converting input mesh formats into the format used by Lizzy.

    Parameters
    ----------
    mesh_path : Path
        The path to the mesh file.

    """
    def __init__(self, ):
        self.mesh_data:dict = {} # A dict containing all the mesh info from the gmsh file
        self.case_name:str = None
        self.mesh_format:Format = None

    def read_mesh_file(self, mesh_path: str | os.PathLike) -> None:
        mesh_path = Path(mesh_path)
        self.case_name = self.__read_case_name(mesh_path)
        logger.info(f" Reading mesh file: {mesh_path}")
        self.mesh_format = self._detect_format(mesh_path)
        match self.mesh_format:
            case Format.MSH:
                self.mesh_data = self._read_gmsh_file(mesh_path)
            case Format.STL:
                self.mesh_data = self._read_stl_file(mesh_path)

    def __read_case_name(self, mesh_path:Path):
        case_name = mesh_path.stem
        return case_name

    def _detect_format(self, mesh_path:Path) -> Format:
        """Detect the mesh format from the file extension."""
        suffix = mesh_path.suffix.lower()
        format_by_suffix = {
            ".msh": Format.MSH,
            ".stl": Format.STL,
        }
        try:
            return format_by_suffix[suffix]
        except KeyError:
            supported = ", ".join(sorted(format_by_suffix))
            raise MeshError(f"Unsupported mesh file format '{suffix}'. Supported formats: {supported}.")

    def _read_gmsh_file(self, mesh_path:Path) -> dict:
        """
        Reads a mesh file in .msh format (ASCII 4). Initialises all mesh attributes.
        """
        try:
            mesh_file = meshio.read(mesh_path, file_format="gmsh")
        except meshio._exceptions.ReadError:
            raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
        
        all_nodes_coords : np.ndarray = mesh_file.points
        physical_domain_names = []
        physical_line_names = []
        nodes_conn = mesh_file.cells_dict["triangle"]
        # get lines conn
        physical_lines_conn = mesh_file.cells_dict["line"]
        # get inlet and vent lines conn
        physical_domains = {}
        physical_lines = {}
        physical_nodes_ids = {}
        for key in mesh_file.cell_sets_dict:
            if 'triangle' in mesh_file.cell_sets_dict[key] and 'gmsh' not in key:
                physical_domains[key] = mesh_file.cell_sets_dict[key]['triangle']
                if key not in physical_domain_names:
                    physical_domain_names.append(key)
            if 'line' in mesh_file.cell_sets_dict[key] and 'gmsh' not in key:
                physical_lines[key] = mesh_file.cell_sets_dict[key]['line']
                if key not in physical_line_names:
                    physical_line_names.append(key)
        # get node ids for nodes in the physical lines
        for key in physical_lines:
            physical_nodes_ids[key] = extract_unique_nodes(mesh_file.cells_dict["line"][physical_lines[key]])
        
        return populate_mesh_data(all_nodes_coords,
                                nodes_conn,
                                physical_lines_conn=physical_lines_conn,
                                physical_domains=physical_domains,
                                physical_lines=physical_lines,
                                physical_nodes_ids=physical_nodes_ids,
                                physical_domain_names=physical_domain_names,
                                physical_line_names=physical_line_names)

    def _read_stl_file(self, mesh_path:Path) -> dict:
        """
        Reads a mesh file in .stl format. STL format carry no named regions, so all
        triangles are placed in a single physical domain named 'STL_DOMAIN'. There are no physical lines.
        """
        try:
            mesh_file = meshio.read(mesh_path, file_format="stl")
        except meshio._exceptions.ReadError:
            raise FileNotFoundError(f"Mesh file not found: {mesh_path}")

        all_nodes_coords : np.ndarray = mesh_file.points
        nodes_conn = mesh_file.cells_dict["triangle"]

        # single default domain covering all triangles
        physical_domains = {"STL_DOMAIN": np.arange(len(nodes_conn))}
        physical_domain_names = ["STL_DOMAIN"]

        return populate_mesh_data(all_nodes_coords,
                                nodes_conn,
                                physical_domains=physical_domains,
                                physical_domain_names=physical_domain_names)

    def print_mesh_info(self) -> None:
        """Returns some information about the mesh.
        """
        format_labels = {Format.MSH: "MSH (v4 ASCII)", Format.STL: "STL"}
        format_label = format_labels.get(self.mesh_format, "unknown")
        info = textwrap.dedent(rf"""
        Mesh file format: {format_label},
        Case name:    {self.case_name}
        Mesh contains {len(self.mesh_data['all_nodes_coords'])} nodes, {len(self.mesh_data['nodes_conn'])} elements.
        Physical domains:        {self.mesh_data['physical_domain_names']}
        Physical lines:          {self.mesh_data['physical_line_names']}
        """)
        print(info)
