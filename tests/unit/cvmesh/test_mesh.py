import pytest
import lizzy
import numpy as np
from lizzy._core.cvmesh.mesh import Mesh
from lizzy.exceptions import MeshError

@pytest.fixture
def mesh():
    model = lizzy.LizzyModel()
    model.read_mesh_file("tests/test_meshes/Rect_1M_64elem.msh")
    model.set_simulation_parameters(output_interval=10000, in_memory_solve=True)
    model.create_resin("resin", 0.1)
    model.assign_resin("resin")
    model.create_material("test_material", (1E-10, 1E-10, 1E-10), 0.5, 0.005)
    model.assign_material("test_material", 'domain')
    model.create_pressure_inlet("inlet_left", 1E+05)
    model.assign_inlet("inlet_left", "left_edge")
    model.initialise_solver()
    return model._mesh

def test_area_coherence(mesh: Mesh):
    # the total empty area calculated from cvs shoulb be the same a sthe total area calculated from the triangles
    tri_area = sum(tri.A for tri in mesh.triangles)
    cv_area = sum(cv.A for cv in mesh.CVs)
    np.testing.assert_allclose(tri_area, cv_area, rtol=1e-12)

def test_volume_coherence(mesh: Mesh):
    # the total empty volume calculated from cvs shoulb be the same a sthe total volume calculated from the triangles
    tri_volume = sum(tri.A*tri.h*tri.porosity for tri in mesh.triangles)
    cv_volume = sum(cv.vol for cv in mesh.CVs)
    np.testing.assert_allclose(tri_volume, cv_volume, rtol=1e-12)

def test_node_triangle_cross_reference(mesh: Mesh):
    # each node should reference the same triangles that reference it
    for node in mesh.nodes:
        assert sorted(node.triangle_ids) == sorted(t.idx for t in node.triangles)

def test_every_node_has_at_least_one_triangle(mesh: Mesh):
    for node in mesh.nodes:
        assert len(node.triangles) > 0

# CV

def test_cv_lines_count(mesh: Mesh):
    # each CV muyst have exactly 2 CVLines per support triangle
    for cv in mesh.CVs:
        total = sum(len(lines) for lines in cv.cv_lines)
        assert total == 2 * len(cv.support_triangles)

def test_cv_flux_normals_outward(mesh: Mesh):
    for cv in mesh.CVs:
        for i, tri in enumerate(cv.support_triangles):
            for cvline in cv.cv_lines[i]:
                d_out = np.linalg.norm(tri.centroid + cvline.n - cv.node.coords)
                d_in  = np.linalg.norm(tri.centroid - cvline.n - cv.node.coords)
                assert d_out >= d_in


# --- Mesh boundary lines ---

def test_boundary_lines_nonzero_length(mesh: Mesh):
    # each boundary line should have length positive > 0
    for bl in mesh.boundary_lines:
        assert bl.length > 0

def test_boundary_line_normals_outward(mesh: Mesh):
    for bl in mesh.boundary_lines:
        tri = mesh.triangles[bl.tri_idx]
        d_out = np.linalg.norm(bl.midpoint + bl.n - tri.centroid)
        d_in  = np.linalg.norm(bl.midpoint - bl.n - tri.centroid)
        assert d_out >= d_in


# --- mesh methods ---

def test_empty_cvs_resets_fill(mesh: Mesh):
    for cv in mesh.CVs:
        cv.fill = 1.0
    mesh.empty_cvs()
    assert all(cv.fill == 0 for cv in mesh.CVs)

def test_assert_all_elements_have_material_raises(mesh: Mesh):
    # manually set one triangle to not assignem material, then run the Mesh method "assert_all_elements_have_material"
    mesh.triangles[0].material_assigned = False
    with pytest.raises(MeshError):
        mesh.assert_all_elements_have_material()

