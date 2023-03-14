import numpy as np
import tkinter as tk
from math import sqrt
from skimage.measure import label

from Advanced_Canvas import Advanced_Polygon


class Data(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, box_size: float, shape: (int, int), colors):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.box_size = box_size
        self.DATA = np.zeros(shape)
        self.GROUPS = np.zeros(shape)

        self.foreground = False
        self.background = False

        self.colors = colors
        self.polygons = {}
        self.polygon_color = {}

        self.canvas_objects = {}

    # change an index of data
    def set_index(self, x: int, y: int, new_index: int):
        assert 0 <= x <= self.DATA.shape[0] and 0 <= y <= self.DATA.shape[1], f"{x}, {y} location does not exist"
        assert 0 <= new_index+1 <= len(self.colors), "index is not in range of colors"

        # change color of pixel
        self.DATA[x, y] = new_index+1

        # group the array
        self.GROUPS = label(self.DATA, connectivity=2)

        # calculate the polygon structure
        self.calc_polygon()

    # calculate the outline of the polygon
    def calc_polygon(self):
        groups = np.unique(self.GROUPS)

        for group_index in groups:
            if group_index != 0:
                # create map
                group = np.pad(np.where(self.GROUPS == group_index, 1, 0), pad_width=1, mode="constant")
                group_idx = np.where(self.GROUPS == group_index)

                # calculate main outline
                corners = self.__calc_outline(group, group_idx[0][0], group_idx[1][0])

                # initialise hole map
                hole_data = np.zeros(self.DATA.shape)

                # Find the minimum and maximum y-coordinates of the corners vertices
                arr_corners = np.array(corners)
                y_min = int(np.floor(arr_corners[:, 1]).min())
                y_max = int(np.ceil(arr_corners[:, 1]).max())

                # Loop over each row in the range of y-coordinates
                for y in range(y_min, y_max + 1):
                    # Find the x-coordinates where the arr_corners edges intersect the row
                    intersections = []
                    for i in range(len(arr_corners)):
                        j = (i + 1) % len(arr_corners)
                        if arr_corners[i, 1] < y and arr_corners[j, 1] >= y or arr_corners[j, 1] < y and arr_corners[i, 1] >= y:
                            x = (y - arr_corners[i, 1]) * (arr_corners[j, 0] - arr_corners[i, 0]) / (
                                        arr_corners[j, 1] - arr_corners[i, 1]) + arr_corners[i, 0]
                            intersections.append(x)

                    # Sort the intersection points in order of increasing x-coordinate
                    intersections.sort()

                    # Append the occupied pixel coordinates to the list
                    for i in range(0, len(intersections), 2):
                        left_pixel = int(np.floor(intersections[i]))
                        right_pixel = int(np.ceil(intersections[i + 1]))
                        for x in range(left_pixel, right_pixel):
                            if self.DATA[x, y-1] == 0:
                                hole_data[x, y-1] = 1

                hole_groups = label(hole_data, connectivity=2)

                hole_outlines = []
                # calculate outlines for holes
                for i in np.unique(hole_groups):
                    if i != 0:
                        # generate specific map
                        group = np.pad(np.where(hole_groups == i, 1, 0), pad_width=1, mode="constant")
                        idx = np.where(hole_groups == i)

                        # calculate outline
                        hole_outlines.append(self.__calc_outline(group, idx[0][0], idx[1][0]))
                
                for out in hole_outlines:
                    closest_dis = [-1, float("inf")]
                    # insert holes to polygon
                    for i, pos in enumerate(corners):
                        if pos[0] <= out[0][0] and pos[1] <= out[0][1] and sqrt((pos[0]-out[0][0])**2+(pos[1]-out[0][1])**2) < closest_dis[1]:
                            closest_dis = [i, sqrt((pos[0]-out[0][0])**2+(pos[1]-out[0][1])**2)]

                    out = [corners[closest_dis[0]]]+out+[out[0]]
                    out.reverse()
                    corners[closest_dis[0]+1:closest_dis[0]+1] = out

                # add corners and color to list
                if str(group_index) in self.polygons:
                    self.polygons[str(group_index)] = [(round(i[0] * self.box_size + self.x), round(i[1] * self.box_size + self.y)) for i in corners]
                    self.polygon_color[str(group_index)] = self.colors[round(self.DATA[group_idx[0][0], group_idx[1][0]])-1]
                else:
                    self.polygons.update({str(group_index): [(round(i[0] * self.box_size + self.x), round(i[1] * self.box_size + self.y)) for i in corners]})
                    self.polygon_color.update({str(group_index): self.colors[round(self.DATA[group_idx[0][0], group_idx[1][0]])-1]})

    @staticmethod
    # find outline
    def __calc_outline(arr, x: int, y: int):
        corners = [(x, y)]
        pos = [x, y+1]
        start = [x, y]
        prev_movement = [0, 1]

        while True:
            if pos != start:
                # 0, 0 oder 1, 0
                # 0, 1 oder 1, 1
                if arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 0], [0, 1]] or arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [1, 1]]:
                    corners.append((pos[0], pos[1]))
                    pos[1] += 1
                    prev_movement = [0, 1]
                # 0, 1
                # 1, 0
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [1, 0]]:
                    # coming from the right
                    if prev_movement == [0, 1]:
                        corners.append((pos[0], pos[1]))
                        pos[0] -= 1
                        prev_movement = [-1, 0]
                    # coming from the left
                    if prev_movement == [0, -1]:
                        corners.append((pos[0], pos[1]))
                        pos[0] += 1
                        prev_movement = [1, 0]
                # 0, 0
                # 1, 1
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 0], [1, 1]]:
                    pos[1] += 1
                    prev_movement = [0, 1]
                # 0, 0 oder 1, 1
                # 1, 0 oder 1, 0
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 0], [1, 0]] or arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 1], [1, 0]]:
                    corners.append((pos[0], pos[1]))
                    pos[0] += 1
                    prev_movement = [1, 0]
                # 1, 0
                # 0, 1
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [0, 1]]:
                    # coming from the top
                    if prev_movement == [1, 0]:
                        corners.append((pos[0], pos[1]))
                        pos[1] += 1
                        prev_movement = [0, 1]
                    # coming from the bottom
                    if prev_movement == [-1, 0]:
                        corners.append((pos[0], pos[1]))
                        pos[1] -= 1
                        prev_movement = [0, -1]
                # 1, 0
                # 1, 0
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [1, 0]]:
                    pos[0] += 1
                    prev_movement = [1, 0]
                # 1, 0 oder 1, 1
                # 0, 0 oder 0, 1
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [0, 0]] or arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 1], [0, 1]]:
                    corners.append((pos[0], pos[1]))
                    pos[1] -= 1
                    prev_movement = [0, -1]
                # 1, 1
                # 0, 0
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 1], [0, 0]]:
                    pos[1] -= 1
                    prev_movement = [0, -1]
                # 0, 1 oder 0, 1
                # 0, 0 oder 1, 1
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [0, 0]] or arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [1, 1]]:
                    corners.append((pos[0], pos[1]))
                    pos[0] -= 1
                    prev_movement = [-1, 0]
                # 0, 1
                # 0, 1
                elif arr[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [0, 1]]:
                    pos[0] -= 1
                    prev_movement = [-1, 0]
            # end loop because we are back at the starting point
            else:
                break

        return corners

    # draw on screen
    def draw(self):
        # clear unnecessary polygons
        for key, value in self.canvas_objects.items():
            if key not in self.polygons:
                value.clear()

        for key, value in self.polygons.items():

            # update polygon corners
            if key not in self.canvas_objects:
                self.canvas_objects.update({key: Advanced_Polygon(self.canvas, value, (0, 0, 0))})
                self.canvas_objects[key].set_color(self.polygon_color[key])
                # set new canvas object to background
                if self.background:
                    self.canvas_objects[key].set_to_background(True)
                elif self.foreground:
                    self.canvas_objects[key].set_to_foreground(True)
            else:
                self.canvas_objects[key].set_pos(value)
                self.canvas_objects[key].set_color(self.polygon_color[key])

            # draw
            self.canvas_objects[key].draw()

    # set position
    def set_pos(self, x: int, y: int):
        # delta
        delta_x, delta_y = x-self.x, y-self.y

        # update class variables
        self.x = x
        self.y = y

        # update positions
        for key, value in self.polygons.items():
            self.polygons[key] = [(i[0]+delta_x, i[1]+delta_y) for i in value]

        # update positions
        for key, value in self.canvas_objects.items():
            value.set_pos(self.polygons[key])

    # set box_size
    def set_box_size(self, box_size: int):
        # update class variable
        self.box_size = box_size

        # calculate polygons
        self.calc_polygon()

    # set to background
    def set_to_background(self, forever=False):
        for key, value in self.canvas_objects.items():
            value.set_to_background(forever)

        self.foreground = False if forever else self.foreground
        self.background = forever

    # set to foreground
    def set_to_foreground(self, forever=False):
        for key, value in self.canvas_objects.items():
            value.set_to_background(forever)

        self.foreground = forever
        self.background = False if forever else self.background
