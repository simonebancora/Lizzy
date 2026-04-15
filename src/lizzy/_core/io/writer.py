#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import shutil
from pathlib import Path
from enum import Enum, auto
import numpy as np
import meshio
import h5py
import textwrap
from lizzy._core.datatypes import Solution

logger = logging.getLogger("lizzy.io")


class Writer:
    """Handles writing results to output files."""
    def __init__(self):
        self._mesh = None
    
    def assign_mesh(self, mesh):
        self._mesh = mesh

    def save_results(self, result_name:str, solution:Solution, **kwargs):
        """Save the results contained in the solution dictionary into an XDMF file.

        Parameters
        ----------
        solution : dict
        result_name : str
            The name of the new folder where results will be saved.
        """
        _format = kwargs.get("format", "xdmf")
        save_cv_mesh = kwargs.get("save_cv_mesh", False)
        save_permeability = kwargs.get("save_permeability", False)
        logger.info(" Saving results...")
        destination_path = Path("results") / result_name
        if os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        os.makedirs(destination_path, exist_ok=True)
        points = self._mesh.node_coords  # Node coordinates, assumed to be (N, 3)
        cells = self._mesh.tri_conn_table  # Triangle connectivity (M, 3)
        cells_list = []
        for i in range(len(cells)) :
            cells_list.append(cells[i])

        if save_cv_mesh:
            mesh_cv = meshio.Mesh(
                points=self._mesh.cv_mesh_nodes,
                cells=[("line", self._mesh.cv_mesh_conn)],  # Triangle connectivity
            )
            mesh_cv.write(destination_path / f"{result_name}_CV.vtk")

        if save_permeability:
            perm = np.array([self._mesh.triangles[i].k for i in range(len(cells))])

        if _format == "xdmf":
            filename = f"{result_name}.xdmf"
            with meshio.xdmf.TimeSeriesWriter(filename) as writer:
                writer.write_points_cells(points, [("triangle", cells_list)])
                for i in range(solution.n_time_states):
                    time = solution.time[i]
                    point_data = {  "Pressure" : solution.p[i],
                                    "FillFactor" : solution.fill_factor[i],
                                    "FreeSurface" : solution.free_surface[i],
                                    "Velocity" : solution.v_nodal[i]
                                 }
                    cell_data = { "Velocity" : solution.v[i] }
                    if save_permeability:
                        cell_data["Permeability"] = perm
                    writer.write_data(time, point_data=point_data, cell_data=cell_data)
            shutil.move(filename, destination_path / filename)
            shutil.move(f"{result_name}.h5", destination_path / f"{result_name}.h5")

        logger.info(f" Results saved in {destination_path}")


class StreamingWriter:
    """Handles incremental writing of results to HDF5/XDMF files during simulation.
    
    Uses open→write→close pattern for each timestep to ensure data integrity
    and allow live viewing of results in ParaView during simulation.
    
    Files are written directly to the results/ folder from the start.
    The HDF5 file is opened in append mode for each write, ensuring no data
    corruption even if the simulation crashes. The XDMF descriptor file is
    regenerated periodically (controlled by xdmf_update_interval) so results
    are viewable during the simulation.
    
    Parameters
    ----------
    xdmf_update_interval : int, optional
        How often to regenerate the XDMF file (every N timesteps). Default: 5.
        Lower values = more responsive live viewing but slower performance.
        Higher values = better performance but less frequent updates.
        XDMF is always written on finalize() regardless of this setting.
    """
    def __init__(self, xdmf_update_interval: int = 5):
        self._mesh = None
        self._result_name: str = None
        self._destination_path: Path = None
        self._xdmf_filepath: Path = None
        self._h5_filepath: Path = None
        self._is_initialized: bool = False
        self._timestep_count: int = 0
        self._save_permeability: bool = False
        self._perm: np.ndarray = None
        self._times: list = []
        self._n_points: int = 0
        self._n_cells: int = 0
        self._xdmf_update_interval: int = xdmf_update_interval
    
    def initialize(self, mesh, result_name: str, save_permeability: bool = False):
        """Initialize the streaming writer and write mesh structure to HDF5.
        
        Creates the results folder and writes files directly there.
        
        Parameters
        ----------
        mesh : Mesh
            The mesh object containing node coordinates and connectivity.
        result_name : str
            Base name for the output files.
        save_permeability : bool, optional
            If True, include permeability as a cell field. Default: False.
        """
        self._mesh = mesh
        self._result_name = result_name
        self._save_permeability = save_permeability
        
        # Create results folder and set file paths
        self._destination_path = Path("results") / result_name
        if os.path.isdir(self._destination_path):
            shutil.rmtree(self._destination_path)
        os.makedirs(self._destination_path, exist_ok=True)
        
        self._xdmf_filepath = self._destination_path / f"{result_name}.xdmf"
        self._h5_filepath = self._destination_path / f"{result_name}.h5"
        
        points = self._mesh.node_coords
        cells = self._mesh.tri_conn_table
        self._n_points = len(points)
        self._n_cells = len(cells)
        
        if save_permeability:
            self._perm = np.array([self._mesh.triangles[i].k for i in range(self._n_cells)])
        
        # Write mesh structure to HDF5 (open→write→close)
        with h5py.File(self._h5_filepath, 'w') as h5file:
            h5file.create_dataset('mesh/points', data=points, dtype='float64')
            h5file.create_dataset('mesh/cells', data=cells, dtype='int64')
        
        self._is_initialized = True
        self._timestep_count = 0
        self._times = []
        logger.info(f" StreamingWriter: writing results to {self._destination_path}")
    
    def append_timestep(self, time: float, p: np.ndarray, v: np.ndarray, 
                        v_nodal: np.ndarray, fill_factor: np.ndarray, 
                        free_surface: np.ndarray):
        """Append a single timestep to the output file.
        
        Opens HDF5 in append mode, writes data, closes file, then regenerates XDMF.
        This ensures data is always safely on disk and viewable.
        
        Parameters
        ----------
        time : float
            Simulation time for this timestep.
        p : np.ndarray
            Pressure field at nodes.
        v : np.ndarray
            Velocity field at elements.
        v_nodal : np.ndarray
            Velocity field at nodes.
        fill_factor : np.ndarray
            Fill factor at nodes.
        free_surface : np.ndarray
            Free surface indicator at nodes.
        """
        if not self._is_initialized:
            raise RuntimeError("StreamingWriter not initialized. Call initialize() first.")
        
        # Open HDF5 in append mode, write timestep data, close
        with h5py.File(self._h5_filepath, 'a') as h5file:
            grp = h5file.create_group(f"data{self._timestep_count}")
            grp.create_dataset('Pressure', data=p.copy(), dtype='float64')
            grp.create_dataset('FillFactor', data=fill_factor.copy(), dtype='float64')
            grp.create_dataset('FreeSurface', data=free_surface.copy(), dtype='float64')
            grp.create_dataset('Velocity_nodal', data=v_nodal.copy(), dtype='float64')
            grp.create_dataset('Velocity_cell', data=v.copy(), dtype='float64')
            if self._save_permeability and self._timestep_count == 0:
                h5file.create_dataset('mesh/Permeability', data=self._perm, dtype='float64')
        
        self._times.append(time)
        self._timestep_count += 1
        
        # Regenerate XDMF periodically so results are viewable during simulation
        if self._timestep_count % self._xdmf_update_interval == 0:
            self._write_xdmf()
    
    def _write_xdmf(self):
        """Generate XDMF descriptor file pointing to HDF5 data.
        
        The XDMF format is compatible with ParaView's Xdmf3ReaderS reader.
        """
        h5_basename = self._h5_filepath.name
        
        lines = [
            '<?xml version="1.0"?>',
            '<Xdmf Version="3.0">',
            '  <Domain>',
            '    <Grid Name="TimeSeries" GridType="Collection" CollectionType="Temporal">'
        ]
        
        for i, t in enumerate(self._times):
            lines.extend([
                f'      <Grid Name="mesh_{i}" GridType="Uniform">',
                f'        <Time Value="{t}"/>',
                f'        <Topology TopologyType="Triangle" NumberOfElements="{self._n_cells}">',
                f'          <DataItem DataType="Int" Dimensions="{self._n_cells} 3" Format="HDF">{h5_basename}:/mesh/cells</DataItem>',
                '        </Topology>',
                '        <Geometry GeometryType="XYZ">',
                f'          <DataItem DataType="Float" Dimensions="{self._n_points} 3" Format="HDF">{h5_basename}:/mesh/points</DataItem>',
                '        </Geometry>',
                # Point data fields
                '        <Attribute Name="Pressure" AttributeType="Scalar" Center="Node">',
                f'          <DataItem DataType="Float" Dimensions="{self._n_points}" Format="HDF">{h5_basename}:/data{i}/Pressure</DataItem>',
                '        </Attribute>',
                '        <Attribute Name="FillFactor" AttributeType="Scalar" Center="Node">',
                f'          <DataItem DataType="Float" Dimensions="{self._n_points}" Format="HDF">{h5_basename}:/data{i}/FillFactor</DataItem>',
                '        </Attribute>',
                '        <Attribute Name="FreeSurface" AttributeType="Scalar" Center="Node">',
                f'          <DataItem DataType="Float" Dimensions="{self._n_points}" Format="HDF">{h5_basename}:/data{i}/FreeSurface</DataItem>',
                '        </Attribute>',
                '        <Attribute Name="Velocity" AttributeType="Vector" Center="Node">',
                f'          <DataItem DataType="Float" Dimensions="{self._n_points} 3" Format="HDF">{h5_basename}:/data{i}/Velocity_nodal</DataItem>',
                '        </Attribute>',
                '        <Attribute Name="CellVelocity" AttributeType="Vector" Center="Cell">',
                f'          <DataItem DataType="Float" Dimensions="{self._n_cells} 3" Format="HDF">{h5_basename}:/data{i}/Velocity_cell</DataItem>',
                '        </Attribute>',
            ])
            if self._save_permeability:
                lines.extend([
                    '        <Attribute Name="Permeability" AttributeType="Tensor" Center="Cell">',
                    f'          <DataItem DataType="Float" Dimensions="{self._n_cells} 3 3" Format="HDF">{h5_basename}:/mesh/Permeability</DataItem>',
                    '        </Attribute>',
                ])
            lines.append('      </Grid>')
        
        lines.extend([
            '    </Grid>',
            '  </Domain>',
            '</Xdmf>'
        ])
        
        with open(self._xdmf_filepath, 'w') as f:
            f.write('\n'.join(lines))
    
    def finalize(self, destination_folder: str = None):
        """Finalize the streaming writer.
        
        Writes the final XDMF file to ensure all timesteps are included,
        then marks the writer as complete.
        
        Parameters
        ----------
        destination_folder : str, optional
            Ignored (kept for API compatibility). Files are already in results/.
        """
        if not self._is_initialized:
            logger.warning(" StreamingWriter.finalize() called but writer was not initialized.")
            return
        
        # Write final XDMF to include all timesteps
        self._write_xdmf()
        
        self._is_initialized = False
        logger.info(f" Results saved in {self._destination_path} ({self._timestep_count} timesteps)")
    
    @property
    def is_initialized(self) -> bool:
        """Returns True if the writer is initialized and ready to accept timesteps."""
        return self._is_initialized
    
    @property
    def timestep_count(self) -> int:
        """Returns the number of timesteps written so far."""
        return self._timestep_count