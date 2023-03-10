import numpy as np
import tkinter as tk
from math import sqrt

from Advanced_Canvas import Advanced_Polygon


class Data(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, box_size: int, shape: (int, int), colors):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.box_size = box_size
        self.DATA = np.zeros(shape)
        self.GROUPS = np.zeros(shape)

        self.colors = colors
        self.polygons = {}

        self.canvas_objects = {}

    # change an index of data
    def set_index(self, x: int, y: int, new_index: int):
        x, y = y, x
        assert 0 <= x <= self.DATA.shape[0] and 0 <= y <= self.DATA.shape[1], f"{x}, {y} location does not exist"
        assert 0 <= new_index < len(self.colors), "index is not in range of colors"

        # update data
        self.DATA[x, y] = new_index
        data = np.pad(self.DATA, pad_width=1, mode="constant")

        added_to_group = False
        # calculate new groups
        if x-1 >= 0 and y-1 >= 0 and self.DATA[x-1, y-1] == new_index:
            self.GROUPS[x, y] = self.GROUPS[x-1, y-1]
            added_to_group = True

        if y-1 >= 0 and self.DATA[x, y-1] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x, y-1]
                added_to_group = True
            elif self.GROUPS[x, y-1] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x, y-1]] = self.GROUPS[x, y]

        if x+2 <= self.DATA.shape[0] and y-1 >= 0 and self.DATA[x+1, y-1] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x+1, y-1]
                added_to_group = True
            elif self.GROUPS[x+1, y-1] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x+1, y-1]] = self.GROUPS[x, y]

        if x+2 <= self.DATA.shape[0] and self.DATA[x+1, y] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x+1, y]
                added_to_group = True
            elif self.GROUPS[x+1, y] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x+1, y]] = self.GROUPS[x, y]

        if x+2 <= self.DATA.shape[0] and y+2 <= self.DATA.shape[1] and self.DATA[x+1, y+1] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x+1, y+1]
                added_to_group = True
            elif self.GROUPS[x+1, y+1] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x+1, y+1]] = self.GROUPS[x, y]

        if y+2 <= self.DATA.shape[1] and self.DATA[x, y+1] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x, y+1]
                added_to_group = True
            elif self.GROUPS[x, y+1] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x, y+1]] = self.GROUPS[x, y]

        if x-1 >= 0 and y+2 <= self.DATA.shape[1] and self.DATA[x-1, y+1] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x-1, y+1]
                added_to_group = True
            elif self.GROUPS[x-1, y+1] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x-1, y+1]] = self.GROUPS[x, y]

        if x-1 >= 0 and self.DATA[x-1, y] == new_index:
            if not added_to_group:
                self.GROUPS[x, y] = self.GROUPS[x-1, y]
                added_to_group = True
            elif self.GROUPS[x-1, y] != self.GROUPS[x, y]:
                self.GROUPS[self.GROUPS == self.GROUPS[x-1, y]] = self.GROUPS[x, y]

        if not added_to_group:
            self.GROUPS[x, y] = np.max(self.GROUPS)+1

    # calculate the outline of the polygon
    def calc_polygon(self):
        groups = np.unique(self.GROUPS)

        for i in groups:
            if i != 0:
                # create new list
                group = np.pad(np.where(self.GROUPS == i, 1, 0), pad_width=1, mode="constant")
                # where 1
                idx = np.where(self.GROUPS == i)

                # find the indices of non-zero elements
                indices = np.argwhere(group)

                # extract the minimum and maximum indices for each dimension
                min_indices = indices.min(axis=0)
                max_indices = indices.max(axis=0)

                new_arr = np.pad(np.where(self.GROUPS == i, 1, 0), pad_width=1, mode="constant")

                # fill surrounding 0 with 1 / merge them to the form
                self.flood_fill(new_arr, 0, 0, 2, 0)
                new_arr = np.where(new_arr == 2, 1, new_arr)

                # sort the holes in to groups
                group_index = 2
                while np.any(new_arr == 0):
                    # flood fill the holes to define group
                    index = np.where(new_arr == 0)
                    self.flood_fill(new_arr, index[0][0], index[1][0], group_index, 0)
                    group_index += 1

                # normalize new_arr
                new_arr = np.where(new_arr == 1, 0, new_arr-1)

                # calculate outlines for holes
                hole_outlines = []
                for i in np.unique(new_arr):
                    if i != 0:
                        # create new list
                        hole = np.where(new_arr == i, 1, 0)
                        index = np.where(hole == 1)

                        hole_outlines.append(self.calc_outline(hole, index[0][0]-1, index[1][0]-1))

                corners = self.calc_outline(group, idx[0][0], idx[1][0])

                # find connection point for hole
                dis_indexes = (None, None)
                dis = float("inf")
                for outline in hole_outlines:
                    for i1, p1 in enumerate(outline):
                        for i2, p2 in enumerate(corners):
                            if sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) < dis:
                                dis = sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
                                dis_indexes = (i1, i2)

                    # add infill to polygon corners
                    new_list = outline[dis_indexes[0]:]+outline[:dis_indexes[0]]
                    new_list.reverse()
                    new_list.append(new_list[0])
                    corners[dis_indexes[1]:dis_indexes[1]] = [corners[dis_indexes[1]]]+new_list

                # add corners to list
                if str(i) in self.polygons:
                    self.polygons[str(i)] = [(i[0] * self.box_size + self.x, i[1] * self.box_size + self.y) for i in corners]
                else:
                    self.polygons.update(
                        {str(i): [(i[0] * self.box_size + self.x, i[1] * self.box_size + self.y) for i in corners]})

    # find outline
    def calc_outline(self, arr, x: int, y: int):
        corners = [(x, y)]
        pos = [x, y+1]
        start = [x, y]
        prev_movement = [0, 1]

        print(arr[start[0]: start[0]+2, start[1]: start[1]+2])

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

    # flood fill
    def flood_fill(self, arr, x: int, y: int, new_val: int, old_val: int):
        if old_val is None:
            old_val = arr[x, y]

        if old_val == new_val:
            return

        arr[x, y] = new_val

        if x > 0 and arr[x - 1, y] == old_val:
            self.flood_fill(arr, x - 1, y, new_val, old_val)
        if x < arr.shape[0] - 1 and arr[x + 1, y] == old_val:
            self.flood_fill(arr, x + 1, y, new_val, old_val)
        if y > 0 and arr[x, y - 1] == old_val:
            self.flood_fill(arr, x, y - 1, new_val, old_val)
        if y < arr.shape[1] - 1 and arr[x, y + 1] == old_val:
            self.flood_fill(arr, x, y + 1, new_val, old_val)

    def draw(self):
        for key, value in self.polygons.items():

            if key not in self.canvas_objects:
                self.canvas_objects.update({key: Advanced_Polygon(self.canvas, value, (0, 0, 0))})
            else:
                self.canvas_objects[key].set_pos(value)

            self.canvas_objects[key].draw()
