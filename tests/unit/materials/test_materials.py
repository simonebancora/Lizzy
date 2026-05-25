import pytest
import numpy as np
from lizzy._core.materials.materials import PorousMaterial, Resin

def test_porous_material_constructor():
    mat = PorousMaterial("mat", (1, 2, 3), 0.5, 0.001)
    # test attributes
    assert mat.assigned == False
    np.testing.assert_array_equal(mat.k_princ, np.diag((1,2,3)))

    # test isotropic detection
    mat_isotropic = PorousMaterial("m", (1e-10, 1e-10, 1e-10), porosity=0.5, thickness=0.001)
    assert mat_isotropic.is_isotropic is True

    # test anisotropic detection
    mat_anisotropic = PorousMaterial("m", (1e-10, 2e-10, 1e-10), porosity=0.5, thickness=0.001)
    assert mat_anisotropic.is_isotropic is False

    # test invalid negative permeability values
    with pytest.raises(ValueError, match="all permeability values must be positive"):
        PorousMaterial("m", (-1e-10, 1e-10, 1e-10), porosity=0.5, thickness=0.001)

def test_resin_constructor():
    # test negative viscosity
    with pytest.raises(ValueError, match="viscosity must be positive"):
        resin = Resin("r", -0.1)
