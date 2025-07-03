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

lizzy_cmap = mcolors.LinearSegmentedColormap.from_list("lizzy_colors", ["white", "orange"])


class Renderer():
    def __init__(self, mesh):
        self.figure_idx = 0
        z_node_coords = mesh.nodes.XYZ[:, 2]
        self._x_resolution = 50
        self.x_node_coords = mesh.nodes.XYZ[:, 0]
        self.y_node_coords = mesh.nodes.XYZ[:, 1]
        self.xmin = self.x_node_coords.min()
        self.xmax = self.x_node_coords.max()
        self.ymin = self.y_node_coords.min()
        self.ymax = self.y_node_coords.max()
        xy_img_ratio = (self.xmax - self.xmin) / (self.ymax - self.ymin)
        self._y_resolution = int(self._x_resolution / xy_img_ratio)
        self.grid_elem_size = ((self.xmax - self.xmin)/self._x_resolution, 1/(self.ymax - self.ymin)/self._y_resolution)
        x_lin = np.linspace(self.xmin, self.xmax, self._x_resolution)
        y_lin = np.linspace(self.ymin, self.ymax, self._y_resolution)
        self.grid_x, self.grid_y =  np.meshgrid(x_lin, y_lin, indexing='ij')
        if np.max(np.abs(z_node_coords)) > 0.01:
            self._can_render = False
        else:
            self._can_render = True
        self.initialise_new_figure()
    
    def initialise_new_figure(self):
        self.figure = None
        self.displayed_img = None
        self.displayed_ax = None
        self.displayed_contour_lines = []
        self.displayed_contour_centroids = []
        self.current_fill_img = None
        self.current_contours = None
        self.current_contour_centroids = None
        plt.ion()
        self.figure = plt.figure(self.figure_idx, clear=True)
        self.displayed_ax = self.figure.add_subplot(autoscale_on=False, xlim=(self.xmin, self.xmax), ylim=(self.ymin, self.ymax))
        self.displayed_ax.set_aspect("equal")
        self.figure_idx += 1


    def compute_fill_image(self, fill_factor_array):
        fill_img = griddata(points=(self.x_node_coords, self.y_node_coords), values=fill_factor_array, xi=(self.grid_x, self.grid_y), method='linear').T
        fill_img[:, 0] = 1
        fill_img[:, -1] = 1
        fill_img[0, :] = 1
        fill_img[-1, :] = 1

        fill_img = (fill_img >= 0.5).astype(float)
        return fill_img

    def compute_flow_front_contours(self, fill_img):
        contours = measure.find_contours(fill_img.T)
        centroids = []
        for contour in contours:
            contour[:, 0] = contour[:, 0] * (self.xmax / self._x_resolution) + self.grid_elem_size[0]/2
            contour[:, 1] = contour[:, 1] * (self.ymax / self._y_resolution) + self.grid_elem_size[1]/2
            centroid_x = contour[:, 0].mean()
            centroid_y = contour[:, 1].mean()
            centroids.append((centroid_x, centroid_y))
        return contours, centroids


    def display_fill(self, fill_img, contours, centroids, time_stamp):
        
        if self.displayed_img is None:
            self.displayed_img = self.displayed_ax.imshow(fill_img, extent=(self.xmin, self.xmax, self.ymin, self.ymax), origin='lower', cmap=lizzy_cmap)
        else:
            self.displayed_img.set_data(fill_img)
        
        self.displayed_ax.set_title(f"Fill factor at time = {time_stamp} s")
        
        # Remove previous contours
        for line in self.displayed_contour_lines:
            line.remove()
        self.displayed_contour_lines = []

        # Plot new contours and save references
        for contour in contours:
            line, = self.displayed_ax.plot(contour[:, 0], contour[:, 1], 'r')
            self.displayed_contour_lines.append(line)
        
        # Remove previous contours
        for centroid in self.displayed_contour_centroids:
            centroid.remove()
        self.displayed_contour_centroids = []

        for centroid in centroids:
            point, = self.displayed_ax.plot(centroid[0], centroid[1], marker='o', color='b', markersize=6)
            self.displayed_contour_centroids.append(point)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    
    def generate_current_fill_image_and_contours(self, fill_factor_array, time_stamp, display_fill = False):
        if self._can_render == False:
            print("Cannot generate fill image. Geometry is not flat")
            return
        fill_img = self.compute_fill_image(fill_factor_array)
        contours, centroids = self.compute_flow_front_contours(fill_img)
        if display_fill:
            self.display_fill(fill_img, contours, centroids, time_stamp)
        self.current_fill_img = fill_img
        self.current_contours = contours
        self.current_contour_centroids = centroids
        