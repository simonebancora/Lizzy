import pytest
import numpy as np

from lizzy._core.materials.rosette import Rosette

def test_constructor():
    r = Rosette("r", (1,0,0))
    # test attributes
    assert r.name == "r"
    np.testing.assert_array_equal(r.u, np.array((1,0,0)))

def test_projection():
    # rosette built with e1 (1,0,0) and e3 (0,0,1)
    e1 = np.array([1,0,0])
    e2 = np.array([0,1,0])
    e3 = np.array([0,0,1])
    r = Rosette("r", e1)
    u, v, w = r.project_along_normal(e3)
    # test dot product with parallel vectors
    np.testing.assert_array_equal(np.array(1), np.abs(np.dot(e1, u)))
    np.testing.assert_array_equal(np.array(1), np.abs(np.dot(e2, v)))
    np.testing.assert_array_equal(np.array(1), np.abs(np.dot(e3, w)))
