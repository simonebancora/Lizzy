#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from dataclasses import dataclass, field

class Node:
    def __init__(self, coords:np.array):
        self.coords = coords
        self.id : int = 0
        self.p : float = 0
        self.triangles = []
        self.triangle_ids = []
        self.lines = []
        self.line_ids = []
        self.nodes = []
        self.node_ids = []
    def __str__(self):
        return "Node ID: " + str(self.id)


class Element2D:
    def __init__(self):
        self.id : int = 0
        self.material_tag : str = ""
        self.A : float = 0
        self.h = 1
        self.k = np.empty((3,3))
        self.grad_N = None
        self.porosity = 0.5
        self.nodes = ()
        self.node_ids = []
        self.nodes_coords : np.ndarray = None
        self.lines = []
        self.line_ids = []
        self.centroid = np.zeros(3)
        self.v = np.zeros((3,1))


class Triangle(Element2D):
    ### Triangle element stuff
    # xi is 'xchi'
    dNdxi = np.array([[-1, -1],
                        [1, 0],
                        [0, 1]])
    def __init__(self, node_1:Node, node_2:Node, node_3:Node):
        super().__init__()
        x = np.array((node_1.coords, node_2.coords, node_3.coords))
        J = np.array([
            [x[1,0]-x[0,0], x[2,0]-x[0,0]],
            [x[1,1]-x[0,1], x[2,1]-x[0,1]],
            [x[1,2]-x[0,2], x[2,2]-x[0,2]]
        ])
        detJ = np.linalg.norm(np.cross(J[:, 0], J[:, 1]))
        dxidX = np.linalg.pinv(J)

        # compute triangle normal, used for rosette projection
        u = x[0,:] - x[1,:]
        v = x[0,:] - x[2,:]
        n = np.linalg.cross(u, v)
        self.n = n / np.linalg.norm(n)
        self.nodes = (node_1, node_2, node_3)
        self.grad_N = (Triangle.dNdxi @ dxidX).T
        self.A = 0.5 * detJ
        self.centroid = x.mean(0)

    def __str__(self):
        return "Triangle element ID: " + str(self.id)

class Quad(Element2D):
    pass
    


class Line:
    def __init__(self, node_1:Node, node_2:Node):
        self.nodes = (node_1, node_2)
        self.id : int = 0
        self.midpoint : np.ndarray = self.ComputeMidPoint()
        self.n : np.ndarray = self.ComputeNormal()
        self.triangles = []
        self.triangle_ids = []

    def ComputeMidPoint(self):
        x1 = self.nodes[0].coords
        x2 = self.nodes[1].coords
        return np.array((x1, x2)).mean(0)

    def ComputeNormal(self):
        x1 = self.nodes[0].coords
        x2 = self.nodes[1].coords
        DX = x1 - x2
        l = np.linalg.norm(DX)
        nx = DX[1]/l
        ny = -DX[0]/l
        nz = 0
        return np.array((nx, ny, nz))


@dataclass
class CV:
    id:int = 0
    node:Node = None
    fill:float = 0
    area:float = 0
    free_surface:int = 0
    support_CVs:list = field(default_factory=list)
    support_lines:list = field(default_factory=list)
    support_nodes:list = field(default_factory=list)
    support_triangles : list = field(default_factory=list)
    edges:list = field(default_factory=list)
    A:float = 0
    vol = 0

    # The CV has this structure:
    #   support_triangles = [tri1, tri2, tri3, ... ]
    #   cv_lines (of each support triangle) = [ [line1, line2], [line1, lined], [line1, line2], ... ]
    #   each line has normal, length
    
    def GetCVLines(self):
        self.cv_lines = []
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
            cv_lines_tri = [CVLine(x1, centroid), CVLine(centroid, x2)]
            self.cv_lines.append(cv_lines_tri)
    
    def CalculateVolFluxes(self, v_array):
        cv_fluxe_per_s = 0
        for i, tri in enumerate(self.support_triangles):
            idx = tri.id
            v = v_array[idx]

            line1 = self.cv_lines[i][0]   # PSEUDO CODE ALL TO CHECK AND RE-WRITE
            line2 = self.cv_lines[i][1]
            
            n1 = line1.n
            n2 = line2.n

            flux = np.dot(v.T, (-n1*line1.l + -n2*line2.l))*tri.h
            cv_fluxe_per_s += flux

        return cv_fluxe_per_s

    @staticmethod
    def polygon_area(points):
        """
        Calculate the area of an irregular polygon using the Shoelace formula.

        :param points: A list of (x, y) tuples representing the vertices of the polygon.
                       The vertices should be provided in order (clockwise or counterclockwise).
        :return: The area of the polygon.
        """
        n = len(points)
        if n < 3:
            raise ValueError("A polygon must have at least 3 points.")

        # Compute the Shoelace formula
        area = 0
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n]  # Next vertex (wrap around)
            area += x1 * y2 - y1 * x2

        return abs(area) / 2



    # TODO: check this is correct :
    def calculate_area_and_volume(self):
        vol = 0
        A = 0
        for tri in self.support_triangles:
            point_main = self.node
            point_centroid = tri.centroid
            elem_side_lines = []
            for line in tri.lines:
                if self.node in line.nodes:
                    elem_side_lines.append(line)  # here we get 2 lines
            x1 = elem_side_lines[0].midpoint
            x2 = elem_side_lines[1].midpoint
            perimeter_points = [point_main.coords[0:2], x1[0:2], point_centroid[0:2], x2[0:2]]

            slice_area = self.polygon_area(perimeter_points)
            slice_vol = slice_area*tri.h*tri.porosity
            A += slice_area
            vol += slice_vol
        self.A = A
        self.vol = vol

    def CheckFluxNormalOrientations(self):
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
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.l = 0
        self.n = None
        self.ComputeLengthAndNormal()
    
    def ComputeLengthAndNormal(self):
        DX = self.p1 - self.p2
        self.midpoint = 0.5*(self.p1 + self.p2)
        self.l = np.linalg.norm(DX)
        self.n = np.array((DX[1]/self.l, -DX[0]/self.l, 0))

