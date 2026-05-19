import pytest
import numpy as np
from lizzy._core.cvmesh.entities import Node, Line, Triangle, CV, CVLine

@pytest.fixture
def xy_tri():
    # right triangle in the xy-plane, with area = 0.5
    n0 = Node(0, 0, 0, 0)
    n1 = Node(1, 0, 0, 1)
    n2 = Node(0, 1, 0, 2)
    return Triangle(n0, n1, n2, Line(n0, n1, 0), Line(n1, n2, 1), Line(n2, n0, 2), 0)

def test_node_constructor():
    coords = np.array([2, 15, 7.99])
    idx = 10
    node = Node(coords[0], coords[1], coords[2], idx)
    assert type(node.coords) == np.ndarray
    np.testing.assert_array_equal(coords, node.coords)

def test_triangle_constructor(xy_tri):
    # oblique triangle
    n0 = Node(1, 0, 0, 0)
    n1 = Node(0, 1, 0, 1)
    n2 = Node(0, 0, 1, 2)
    l01 = Line(n0, n1, 10)
    l12 = Line(n1, n2, 11)
    l20 = Line(n2, n0, 12)
    tri = Triangle(n0, n1, n2, l01, l12, l20, 10)

    b = np.sqrt(2)
    h = np.sqrt((0.5 * np.sqrt(2)) ** 2 + 1)
    np.testing.assert_equal(tri.A, b * h / 2)
    mag = np.linalg.norm(np.array([1, 1, 1]))
    np.testing.assert_almost_equal(np.abs(np.dot(tri.n, np.array([1 / mag, 1 / mag, 1 / mag]))), 1.0)
    # test centroid on the xy triangle
    np.testing.assert_allclose(xy_tri.centroid, [1/3, 1/3, 0.0])    

def test_shape_functions(xy_tri):
    # sum of shape function gradients must be zero
    np.testing.assert_allclose(xy_tri.grad_N.sum(axis=1), 0.0, atol=1e-12)
    # grad_N @ nodal values
    node_x = np.array([n.coords[0] for n in xy_tri.nodes])
    np.testing.assert_allclose(xy_tri.grad_N @ node_x, [1.0, 0.0, 0.0], atol=1e-12)
    node_y = np.array([n.coords[1] for n in xy_tri.nodes])
    np.testing.assert_allclose(xy_tri.grad_N @ node_y, [0.0, 1.0, 0.0], atol=1e-12)


def test_line_length_and_midpoint():
    n0 = Node(0, 0, 0, 0)
    n1 = Node(2, 4, 6, 1)
    line = Line(n0, n1, 0)
    np.testing.assert_allclose(line.length, np.linalg.norm(n1.coords - n0.coords))
    np.testing.assert_allclose(line.midpoint, [1.0, 2.0, 3.0])


def test_cv_polygon_area_3d_known_shapes():
    cv = CV(Node(0, 0, 0, 0))
    right_triangle = [np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0])]
    np.testing.assert_allclose(cv._polygon_area_3d(right_triangle), 0.5)
    unit_square = [np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]),
                   np.array([1.0, 1.0, 0.0]), np.array([0.0, 1.0, 0.0])]
    np.testing.assert_allclose(cv._polygon_area_3d(unit_square), 1.0)


def test_cvline_normal_perpendicular_and_unit_length():
    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([1.0, 0.0, 0.0])
    cvline = CVLine(p1, p2, tri_normal=np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(np.linalg.norm(cvline.n), 1.0, atol=1e-12)
    np.testing.assert_allclose(np.dot(cvline.n, p2 - p1), 0.0, atol=1e-12)

