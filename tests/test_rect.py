#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import lizzy as liz
import pytest

tol_err = 0.001
@pytest.fixture()
def mesh():
    mesh_reader = liz.Reader("tests/test_meshes/Rect_1M_R1.msh")
    liz.ProcessParameters.assign(mu=0.1, wo_delta_time=100)
    material_1 = liz.PorousMaterial(1E-10, 1E-10, 1E-10, 0.5, 1.0)
    liz.MaterialManager.add_material('domain', material_1)
    mesh = liz.Mesh(mesh_reader)
    return mesh

def test_fill_1bar(mesh: liz.Mesh):
    analytical_solution = 2500
    bc_manager = liz.BCManager()
    inlet_1 = liz.Inlet('left_edge', 1E+05)
    bc_manager.add_inlet(inlet_1)
    solver = liz.Solver(mesh, bc_manager, liz.SolverType.DIRECT_SPARSE)
    solution = solver.solve(log="off")
    fill_time = solution["time"][-1]
    assert abs(fill_time - analytical_solution) / analytical_solution < tol_err

def test_fill_01bar(mesh: liz.Mesh):
    analytical_solution = 25000
    bc_manager = liz.BCManager()
    inlet_1 = liz.Inlet('left_edge', 1E+04)
    bc_manager.add_inlet(inlet_1)
    solver = liz.Solver(mesh, bc_manager, liz.SolverType.DIRECT_SPARSE)
    solution = solver.solve(log="off")
    fill_time = solution["time"][-1]
    assert abs(fill_time - analytical_solution) / analytical_solution < tol_err