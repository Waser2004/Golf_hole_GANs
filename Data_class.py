import numpy as np
import tkinter as tk

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

    def calc_polygon(self):
        groups = np.unique(self.GROUPS)

        for i in groups:
            if i != 0:
                # create new list
                group = np.pad(np.where(self.GROUPS == i, 1, 0), pad_width=1, mode="constant")
                # different parameters
                idx = np.where(self.GROUPS == i)
                pos = [idx[0][0], idx[1][0]]
                prev_movement = [0, 1]
                corners = []
                end = False

                # define starting point
                start = [pos[0], pos[1]]
                corners.append((pos[0], pos[1]))
                pos[1] += 1

                while not end:
                    if pos != start:
                        # 0, 0 oder 1, 0
                        # 0, 1 oder 1, 1
                        if group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 0], [0, 1]] or group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [1, 1]]:
                            corners.append((pos[0], pos[1]))
                            pos[1] += 1
                            prev_movement = [0, 1]
                        # 0, 1
                        # 1, 0
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [1, 0]]:
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
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 0], [1, 1]]:
                            pos[1] += 1
                            prev_movement = [0, 1]
                        # 0, 0 oder 1, 1
                        # 1, 0 oder 1, 0
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 0], [1, 0]] or group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 1], [1, 0]]:
                            corners.append((pos[0], pos[1]))
                            pos[0] += 1
                            prev_movement = [1, 0]
                        # 1, 0
                        # 0, 1
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [0, 1]]:
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
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [1, 0]]:
                            pos[0] += 1
                            prev_movement = [1, 0]
                        # 1, 0 oder 1, 1
                        # 0, 0 oder 0, 1
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 0], [0, 0]] or group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 1], [0, 1]]:
                            corners.append((pos[0], pos[1]))
                            pos[1] -= 1
                            prev_movement = [0, -1]
                        # 1, 1
                        # 0, 0
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[1, 1], [0, 0]]:
                            pos[1] -= 1
                            prev_movement = [0, -1]
                        # 0, 1 oder 0, 1
                        # 0, 0 oder 1, 1
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [0, 0]] or group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [1, 1]]:
                            corners.append((pos[0], pos[1]))
                            pos[0] -= 1
                            prev_movement = [-1, 0]
                        # 0, 1
                        # 0, 1
                        elif group[pos[0]: pos[0]+2, pos[1]: pos[1]+2].tolist() == [[0, 1], [0, 1]]:
                            pos[0] -= 1
                            prev_movement = [-1, 0]
                    # end loop because we are back at the starting point
                    else:
                        end = True
                        # add corners to list
                        if str(i) in self.polygons:
                            self.polygons[str(i)] = [(i[0]*self.box_size+self.x, i[1]*self.box_size+self.y) for i in corners]
                        else:
                            self.polygons.update({str(i): [(i[0]*self.box_size+self.x, i[1]*self.box_size+self.y) for i in corners]})

    def draw(self):
        for key, value in self.polygons.items():

            if key not in self.canvas_objects:
                self.canvas_objects.update({key: Advanced_Polygon(self.canvas, value, (0, 0, 0))})
            else:
                self.canvas_objects[key].set_pos(value)

            self.canvas_objects[key].draw()