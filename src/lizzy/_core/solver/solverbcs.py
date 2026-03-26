#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.gates import GatesManager
    from lizzy._core.cvmesh import Mesh
    from lizzy._core.materials import MaterialManager

import numpy as np
from lizzy.exceptions import MeshError
from lizzy._core.gates.gates import InletType

class SolverBCs:
    __slots__ = ("dirichlet_idx", "dirichlet_vals", "neumann_idx", "neumann_vals", "p0_idx", "p0_val")

    def __init__(self):
        self.dirichlet_idx = np.empty(0, dtype=np.uint32)
        self.dirichlet_vals = np.empty(0, dtype=np.float64)
        self.neumann_idx = np.empty(0, dtype=np.uint32)
        self.neumann_vals = np.empty(0, dtype=np.float64)
        self.p0_idx = np.empty(0, dtype=np.uint32)
        self.p0_val = 0.0
    
    def update(self, mesh:Mesh, material_manager:MaterialManager, gates_manager:GatesManager):
        # TODO this is more "update inlet dirichlet bcs" since it only applies pressure (doesn't add empty 0 pressure). It can be faster, but it doesn't run often (only at beginning of time intervals) so it's not critical
        self.dirichlet_idx = np.empty(0, dtype=np.uint32)
        self.dirichlet_vals = np.empty(0, dtype=np.float64)
        self.neumann_idx = np.empty(0, dtype=np.uint32)
        self.neumann_vals = np.empty(0, dtype=np.float64)
        dirichlet_idxs = []
        dirichlet_vals = []
        neumann_idxs_pairs = []
        neumann_vals_per_idx_pair = []
        dict_boundary_name_to_inlet_obj = gates_manager._assigned_inlets
        phys_boundary_names_set = mesh.mesh_view.phys_boundary_names_set
        viscosity = material_manager.assigned_resin.mu
        for boundary_name, inlet in dict_boundary_name_to_inlet_obj.items():
            if boundary_name not in phys_boundary_names_set:
                raise MeshError(f"Mesh does not contain physical tag: '{boundary_name}'.")
            match inlet.type:
                case InletType.PRESSURE:
                    node_idxs = mesh.mesh_view.phys_boundary_name_to_node_idxs[boundary_name]
                    if inlet.is_open:
                        # TODO: BUG: we will have a problem here if 2 different boundary edges with bcs applied share a common node...
                        dirichlet_idxs.append(node_idxs)
                        dirichlet_vals.append(np.full(len(node_idxs), inlet.p_value, dtype=np.float64))
                case InletType.FLOW_RATE:
                    boundary_line_idxs = mesh.mesh_view.phys_boundary_name_to_boundary_line_idxs[boundary_name]
                    boundary_line_objs = [mesh.boundary_lines[i] for i in boundary_line_idxs]
                    tri_objs = [mesh.triangles[line.idx] for line in boundary_line_objs]
                    boundary_line_thicknesses = np.array([tri.h for tri in tri_objs])
                    boundary_line_lengths = np.array([line.length for line in boundary_line_objs])
                    boundary_flux_areas = boundary_line_thicknesses * boundary_line_lengths
                    total_area = np.sum(boundary_flux_areas)
                    node_pairs_idxs = mesh.mesh_view.boundary_line_idx_to_node_idxs[boundary_line_idxs] # gives 2 node idxs. At this point, node_pair_idxs (n_lines, 2) and line_lengths (n_lines, ) are in the same order - shape: (n_neumann_lines, 2)
                    neumann_vals_pairs = np.repeat(boundary_flux_areas/2, 2) * (inlet.q_value/total_area)
                    neumann_vals_pairs = neumann_vals_pairs.reshape(len(node_pairs_idxs), 2)
                    if inlet.is_open:
                        neumann_idxs_pairs.append(node_pairs_idxs)
                        neumann_vals_per_idx_pair.append(neumann_vals_pairs)
                    print("Note: Flow rate BC is experimental.")
                case _:
                    pass
        if len(dirichlet_idxs) > 0:
            self.dirichlet_idx = np.concatenate(dirichlet_idxs)
            self.dirichlet_vals = np.concatenate(dirichlet_vals)
        if len(neumann_idxs_pairs) > 0:
            self.neumann_idx = np.concatenate(neumann_idxs_pairs).flatten()
            self.neumann_vals = np.concatenate(neumann_vals_per_idx_pair).flatten()
        
        # assign vacuum vent pressure if vent exists
        if len(gates_manager._assigned_vents) > 0:
            vent_obj = next(iter(gates_manager._assigned_vents.values()))
            self.p0_val = vent_obj.vacuum_pressure
        else:
            self.p0_val = 0.0