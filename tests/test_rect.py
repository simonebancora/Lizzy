#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import lizzy as liz
import pytest

tol_err = 0.01
@pytest.fixture()
def model():
    model = liz.LizzyModel()
    model.read_mesh_file("tests/test_meshes/Rect_1M_R1.msh")
    model.assign_simulation_parameters(mu=0.1, wo_delta_time=100, fill_tolerance=0.00)
    model.create_material(1E-10, 1E-10, 1E-10, 0.5, 1.0, "test_material")
    model.assign_material("test_material", 'domain')
    return model

def test_fill_1bar(model: liz.LizzyModel):
    analytical_solution = 2500
    model.create_inlet(1E+05, "inlet_left")
    model.assign_inlet("inlet_left", "left_edge")
    model.initialise_solver()
    solution = model.solve()
    fill_time = solution.time[-1]
    assert abs(fill_time - analytical_solution) / analytical_solution < tol_err

def test_fill_01bar(model: liz.LizzyModel):
    analytical_solution = 25000
    model.create_inlet(1E+04, "inlet_left")
    model.assign_inlet("inlet_left", "left_edge")
    model.initialise_solver()
    solution = model.solve()
    fill_time = solution.time[-1]
    assert abs(fill_time - analytical_solution) / analytical_solution < tol_err