#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from scipy.linalg import solve
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

def solve_pressure_direct_dense(k, f):
    p = solve(k, f)
    return p.flatten()

def solve_pressure_direct_sparse(k:np.ndarray, f:np.ndarray):
    k_sparse = csr_matrix(k)
    p = spsolve(k_sparse, f)
    return p