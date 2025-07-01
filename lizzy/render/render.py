#  Copyright 2025-2025 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

from scipy.interpolate import griddata
from skimage import measure
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

cmap = mcolors.LinearSegmentedColormap.from_list("lizzy_colors", ["white", "orange"])

def display_fill(mesh, fill_factor_array, time_stamp):
    z_node_coords = mesh.nodes.XYZ[:, 2]
    if np.max(np.abs(z_node_coords)) > 0.01:
        print("Cannot display fill. Geometry is not flat")
        return
    x_node_coords = mesh.nodes.XYZ[:, 0]
    y_node_coords = mesh.nodes.XYZ[:, 1]
    xmin = x_node_coords.min()
    xmax = x_node_coords.max()
    ymin = y_node_coords.min()
    ymax = y_node_coords.max()
    grid_x, grid_y = np.mgrid[xmin:xmax:200j, ymin:ymax:100j]  # 200x200 resolution
    Z = griddata(points=(x_node_coords, y_node_coords), values=fill_factor_array, xi=(grid_x, grid_y), method='linear')
    contours = measure.find_contours(Z)
    plt.figure()
    plt.imshow(Z.T, extent=(xmin, xmax, ymin, ymax), origin='lower', cmap=cmap)
    for contour in contours:
        plt.plot(contour[:, 0] * (xmax / 200), contour[:, 1] * (ymax / 100), 'r')  # Rescale to original domain
    # plt.scatter(x_node_coords, y_node_coords, s=5, c=latest_fill_factor_array, cmap='coolwarm', alpha=0.5)
    plt.title(f"Fill factor at time = {time_stamp} s")
    plt.colorbar(label='fill factor')
    plt.show()