#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import shutil
from pathlib import Path
from enum import Enum, auto
import numpy as np
import meshio
import textwrap
from lizzy._core.datatypes import Solution


class Writer:
    """
    Handles writing results to output files.

    Attributes
    ----------
    mesh : lizzy.Mesh
        The Mesh object used in the simulation.
    """
    def __init__(self, mesh):
        """Class constructor

        Parameters
        ----------
        mesh : lizzy.Mesh
            The Mesh object of the simulation
        """
        self.mesh = mesh

    def save_results(self, solution:Solution, result_name:str, **kwargs):
        """Save the results contained in the solution dictionary into an XDMF file.

        Parameters
        ----------
        solution : dict
        result_name : str
            The name of the new folder where results will be saved.
        """
        _format = kwargs.get("format", "xdmf")
        save_cv_mesh = kwargs.get("save_cv_mesh", False)
        print("\nSaving results...")
        destination_path = Path("results") / result_name
        if os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        os.makedirs(destination_path, exist_ok=True)
        points = self.mesh.nodes.XYZ  # Node coordinates, assumed to be (N, 3)
        cells = self.mesh.triangles.nodes_conn_table  # Triangle connectivity (M, 3)
        cells_list = []
        for i in range(len(cells)) :
            cells_list.append(cells[i])

        if save_cv_mesh:
            mesh_cv = meshio.Mesh(
                points=self.mesh.cv_mesh_nodes,
                cells=[("line", self.mesh.cv_mesh_conn)],  # Triangle connectivity
            )
            mesh_cv.write(destination_path / f"{result_name}_CV.vtk")

        if _format == "xdmf":
            filename = f"{result_name}.xdmf"
            with meshio.xdmf.TimeSeriesWriter(filename) as writer:
                writer.write_points_cells(points, [("triangle", cells_list)])
                for i in range(solution.time_steps_in_solution):
                    time = solution.time[i]
                    point_data = {  "Pressure" : solution.p[i],
                                    "FillFactor" : solution.fill_factor[i],
                                    "FreeSurface" : solution.free_surface[i],
                                    "Velocity" : solution.v_nodal[i]
                                 }
                    cell_data = { "Velocity" : solution.v[i] }
                    writer.write_data(time, point_data=point_data, cell_data=cell_data)
            shutil.move(filename, destination_path / filename)
            shutil.move(f"{result_name}.h5", destination_path / f"{result_name}.h5")

        print(f"Results saved in {destination_path}")