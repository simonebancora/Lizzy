#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.



from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lizzy._core.cvmesh.entities import Node, Line, Triangle, CV
import numpy as np


class Node:
    """Class representing a mesh node."""

    __slots__ = (
        "coords",
        "idx",
        "p",
        "triangles",
        "triangle_ids",
        "lines",
        "line_ids",
        "nodes",
        "node_ids"
    )

    def __init__(self, x: float, y: float, z: float, idx:int):
        self.coords = np.array([x, y, z])
        self.idx : int = idx
        self.p : float = 0
        self.triangles : list[Triangle] = []
        self.triangle_ids : list[int] = []
        self.lines : list[Line] = []
        self.line_ids : list[int] = []
        self.nodes : list[Node] = []
        self.node_ids : list[int] = []
    def __str__(self):
        return "Node ID: " + str(self.idx)
    
    def assign_triangle(self, triangle:Triangle):
        self.triangles.append(triangle)
        self.triangle_ids.append(triangle.idx)



class Element2D:

    __slots__ = (
        "idx",
        "material_tag",
        "A",
        "h",
        "k",
        "grad_N",
        "porosity",
        "nodes",
        "node_ids",
        "nodes_coords",
        "lines",
        "line_ids",
        "centroid",
        "v"
    )

    def __init__(self):
        self.idx : int = 0
        self.material_tag : str = ""
        self.A : float = 0
        self.h = 1
        self.k = np.empty((3,3))
        self.grad_N = None
        self.porosity = 0.5
        self.nodes : tuple[Node] = ()
        self.node_ids : list[int] = []
        self.nodes_coords : np.ndarray = None
        self.lines : tuple[Line] = []
        self.line_ids : list[int] = []
        self.centroid = np.zeros(3)
        self.v : np.ndarray = np.zeros((3,1))

class Triangle(Element2D):
    """Class representing a triangular element.
    """
    ### Triangle element stuff
    # xi is 'xchi'
    dNdxi = np.array([[-1, -1],
                        [1, 0],
                        [0, 1]])
    def __init__(self, node_1:Node, node_2:Node, node_3:Node, line_1:Line, line_2:Line, line_3:Line, n:int):
        super().__init__()
        self.idx = n
        self.nodes = (node_1, node_2, node_3)
        self.node_ids = (node_1.idx, node_2.idx, node_3.idx)
        self.lines = (line_1, line_2, line_3)
        self.line_ids = (line_1.idx, line_2.idx, line_3.idx)
        x = np.array((node_1.coords, node_2.coords, node_3.coords))
        J = np.array([
            [x[1,0]-x[0,0], x[2,0]-x[0,0]],
            [x[1,1]-x[0,1], x[2,1]-x[0,1]],
            [x[1,2]-x[0,2], x[2,2]-x[0,2]]
        ]) # shape 3,2
        detJ = np.linalg.norm(np.cross(J[:, 0], J[:, 1]))
        dxidX = np.linalg.pinv(J)

        # compute triangle normal, used for rosette projection
        u = x[0,:] - x[1,:]
        v = x[0,:] - x[2,:]
        n = np.cross(u, v)
        self.n = n / np.linalg.norm(n)
        self.grad_N = (Triangle.dNdxi @ dxidX).T
        self.A = 0.5 * detJ
        self.centroid = x.mean(0)

    def __str__(self):
        return "Triangle element ID: " + str(self.idx)

class Quad(Element2D):
    pass
    
class Element3D:
    def __init__(self):
        self.idx : int = 0
        self.material_tag : str = ""
        self.volume : float = 0
        self.k = np.empty((3,3))
        self.grad_N = None
        self.porosity = 0.5
        self.nodes = ()
        self.node_ids = []
        self.nodes_coords : np.ndarray = None
        self.faces = []
        self.face_ids = []
        self.centroid = np.zeros(3)
        self.v : np.ndarray = np.zeros((3,1))

class Tetrahedron(Element3D):
    # Shape function derivatives wrt local coordinates (ξ, η, ζ)
    dNdXi = np.array([
        [-1, -1, -1],
        [ 1,  0,  0],
        [ 0,  1,  0],
        [ 0,  0,  1]
    ])

    def __init__(self, node_1:Node, node_2:Node, node_3:Node, node_4:Node):
        super().__init__()
        x = np.array((node_1.coords, node_2.coords, node_3.coords, node_4.coords))
        self.nodes = (node_1, node_2, node_3, node_4)

        J = np.array([
            x[1] - x[0],
            x[2] - x[0],
            x[3] - x[0]
        ]).T  # shape 3,3

        detJ = np.linalg.det(J)
        if detJ <= 0:
            raise ValueError("Tetrahedron has zero or negative volume; check node ordering.")
        self.volume = detJ / 6.0

        dxidX = np.linalg.inv(J)

        # Shape function gradients in global coords
        self.grad_N = (Tetrahedron.dNdXi @ dxidX).T

        # Centroid
        self.centroid = x.mean(axis=0)

        # Faces defined by node indices
        self.faces = [
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 3)
        ]

    def __str__(self):
        return f"Tetrahedron element ID: {self.idx}"

class Line:
    """Class representing a line between two nodes in the mesh.
    """

    __slots__ = (
        "idx",
        "nodes",
        "triangles",
        "triangle_ids",
        "midpoint"
    )
    def __init__(self, node_1:Node, node_2:Node, n):
        self.nodes = (node_1, node_2)
        self.idx : int = n
        self.triangles = []
        self.triangle_ids = []
        self.midpoint : np.ndarray = self._compute_midpoint()

    def _compute_midpoint(self):
        x1 = self.nodes[0].coords
        x2 = self.nodes[1].coords
        return np.array((x1, x2)).mean(0)


class CV:
    """Class representing a control volume in the mesh.
    """
    def __init__(self, node:Node):
        self.node : Node = node
        self.idx : int = node.idx
        self.fill : float = 0
        self.area : float = 0
        self.free_surface : int = 0
        self.support_CVs : list[CV] = []
        self.support_lines : list[Line] = []
        self.support_nodes : list[Node] = []
        self.support_node_ids = None
        self.support_triangles : list[Triangle] = node.triangles
        self.support_triangle_ids = None
        self.edges = []
        self.cv_lines = self._create_cv_lines()
        self.A, self.vol = self._calculate_area_and_volume()
        self._check_flux_normals()
    

    # The CV has this structure:
    #   support_triangles = [tri1, tri2, tri3, ... ]
    #   cv_lines (of each support triangle) = [ [line1, line2], [line1, lined], [line1, line2], ... ]
    #   each line has normal, length
    
    def _create_cv_lines(self):
        cv_lines = []
        for tri in self.support_triangles:
            elem_side_lines = []
            for line in tri.lines:
                if self.node in line.nodes:
                    elem_side_lines.append(line) # here we get 2 lines
            if len(elem_side_lines) != 2:
                print("ERROR: wrong lines fetching")
                exit(0)
            
            # now we have the 2 side lines, we need to create new lines one by one by mid and cog
            x1 = elem_side_lines[0].midpoint
            x2 = elem_side_lines[1].midpoint
            centroid = tri.centroid
            cv_lines_tri = [CVLine(x1, centroid, tri.n), CVLine(centroid, x2, tri.n)]
            cv_lines.append(cv_lines_tri)
        return cv_lines

    def compute_flux_terms(self): # this computes flux_terms, which is an array of variable size (len = n support triangles)
        n_support_triangles = len(self.support_triangles)
        flux_terms = np.empty((n_support_triangles, 3))
        for i in range(n_support_triangles):
            tri = self.support_triangles[i]
            line1 = self.cv_lines[i][0]  # PSEUDO CODE ALL TO CHECK AND RE-WRITE
            line2 = self.cv_lines[i][1]
            n1 = line1.n
            n2 = line2.n
            flux_term = (-n1 * line1.l + -n2 * line2.l) * tri.h
            flux_terms[i] = flux_term
        return flux_terms

    def _polygon_area_3d(self, points):
        """
        Compute the area of a planar polygon in 3D using a generalized Shoelace formula.

        points: A list of 3D points (numpy arrays or length-3 sequences).
        return: area (float)
        """
        pts = [np.array(p, dtype=float) for p in points]
        n = len(pts)
        if n < 3:
            raise ValueError("A polygon must have at least 3 points.")

        # 1. Compute the plane normal using the first three non-collinear points
        # (Assumes input is planar)
        normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        norm_len = np.linalg.norm(normal)
        if norm_len == 0:
            raise ValueError("Points are collinear; polygon has no area.")
        normal /= norm_len  # unit normal

        # 2. Accumulate cross products like Shoelace generalized to 3D
        cross_sum = np.zeros(3)
        for i in range(n):
            p1 = pts[i]
            p2 = pts[(i + 1) % n]
            cross_sum += np.cross(p1, p2)

        # 3. Area = 1/2 * | dot(normal, cross_sum) |
        area = 0.5 * abs(np.dot(normal, cross_sum))
        return area

    # TODO: check if this is correct :
    def _calculate_area_and_volume(self) -> tuple[float, float]:
        area = 0
        vol = 0
        for tri in self.support_triangles:
            point_main = self.node
            point_centroid = tri.centroid
            elem_side_lines = []
            for line in tri.lines:
                if self.node in line.nodes:
                    elem_side_lines.append(line)  # here we get 2 lines
            x1 = elem_side_lines[0].midpoint
            x2 = elem_side_lines[1].midpoint
            perimeter_points = [point_main.coords, x1, point_centroid, x2]

            slice_area = self._polygon_area_3d(perimeter_points)
            slice_vol = slice_area*tri.h*tri.porosity
            area += slice_area
            vol += slice_vol
        return area, vol

    def recalculate_volume(self):
        """Recalculate the CV volume after material properties (porosity, thickness) have been assigned to elements."""
        self.A, self.vol = self._calculate_area_and_volume()

    def _check_flux_normals(self):
        # by convention, normals are oriented outwards from the CV. This function checks and enforces that
        for i, tri in enumerate(self.support_triangles):
            for line in self.cv_lines[i]:
                normal = line.n
                test_point_outer = tri.centroid + normal
                dist_outer = np.linalg.norm(test_point_outer-self.node.coords)
                test_point_inner = tri.centroid - normal
                dist_inner = np.linalg.norm(test_point_inner - self.node.coords)
                if dist_outer < dist_inner:
                    line.n = -line.n

class CVLine:
    def __init__(self, p1, p2, tri_normal):
        self.p1 = p1
        self.p2 = p2
        self.tri_normal = tri_normal
        self.l = self._compute_length()
        self.n = self._compute_normal()
    
    def _compute_length(self):
        d = self.p1 - self.p2
        self.midpoint = 0.5*(self.p1 + self.p2)
        return np.linalg.norm(d)
    
    def _compute_normal(self):
        d = self.p1 - self.p2
        n = np.cross(self.tri_normal, d)
        return n / np.linalg.norm(n)