import copy
import csv
import ast
import cv2
import matplotlib.pyplot as plt
import numpy as np
from math import *


class Data_converter(object):
    def __init__(self, grid_size: tuple[int, int], box_size: int):
        # set grid parameters
        self.GRID_SIZE = grid_size
        self.BOX_SIZE = box_size

        # colors
        self.colors = [
            (50, 205, 50),
            (104, 155, 64),
            (33, 153, 50),
            (20, 101, 33),
            (17, 76, 25),
            (210, 180, 140),
            (240, 230, 140),
            (17, 48, 25),
            (70, 130, 180),
            (255, 255, 255),
            (128, 128, 128),
            (226, 114, 91)
        ]

        # load data
        with open("Data_set/Dataset.csv", "r") as csv_file:
            reader = csv.reader(csv_file)
            rows = [row for row in reader if row]

        self.data = [
            [
                row[0],
                float(row[1]),
                ast.literal_eval(row[2]),
                ast.literal_eval(row[3]),
                ast.literal_eval(row[4]),
                ast.literal_eval(row[5]),
                ast.literal_eval(row[6])
            ]
            for row in rows
        ]
        self.outlines = [[] for _ in self.data]

        # numpy arrays
        self.poly_array = np.zeros((self.GRID_SIZE[1], self.GRID_SIZE[0]), dtype=np.int32)
        self.fade_array = np.zeros((self.GRID_SIZE[1], self.GRID_SIZE[0]), dtype=np.int32)

        # converted data dict
        self.converted_data = {}

    # convert all data
    def convert_all(self):
        # convert data
        for index, data in enumerate(self.data):
            self.convert(data=data)

        # return data
        return list(self.converted_data.values())

    # convert one data set
    def convert(self, data=None, index: int = None):
        assert data is not None or index is not None, "No data specified set an index or hand over data"

        # convert index to data
        if data is None and index is not None:
            data = self.data[index]
        # set index
        if data is not None:
            index = self.data.index(data)

        # only convert data if it hadn't been converted yet
        if not f"{index}" in self.converted_data:
            for d_index, d in enumerate(data[4]):
                # calculate outline
                self.outlines[index].append(self.calc_outline(d))

            # center the outlines
            min_x = min([pos[0] for outline in self.outlines[index] for pos in outline])
            max_x = max([pos[0] for outline in self.outlines[index] for pos in outline])
            min_y = min([pos[1] for outline in self.outlines[index] for pos in outline])
            max_y = max([pos[1] for outline in self.outlines[index] for pos in outline])

            # delta x/y
            delta_x = - ((max_x - min_x) / 2 + min_x)
            delta_y = - ((max_y - min_y) / 2 + min_y)

            # calculate offset
            for i, outline in enumerate(self.outlines[index]):
                self.outlines[index][i] = [[pos[0] + delta_x, pos[1] + delta_y] for pos in outline]

                # convert map data to meters
                for p_index, pos in enumerate(self.outlines[index][i]):
                    # scale outlines
                    self.outlines[index][i][p_index][0] *= data[1] / self.BOX_SIZE
                    self.outlines[index][i][p_index][1] *= data[1] / self.BOX_SIZE

                    # translate to canvas center
                    self.outlines[index][i][p_index][0] += self.GRID_SIZE[0] / 2
                    self.outlines[index][i][p_index][1] += self.GRID_SIZE[1] / 2

                # convert outline to cv2 format points
                points = np.array(self.outlines[index][i], dtype=np.int32)
                points = points.reshape((-1, 1, 2))
                # draw polygon
                cv2.fillPoly(self.poly_array, [points], color=data[6][i]+1)

                # draw fade
                for fade_index, fade in enumerate(data[5][i]):
                    # normal direction
                    if not fade[2]:
                        if fade[0] < fade[1]:
                            fade_points = self.outlines[index][i][fade[0]:fade[1]]
                        else:
                            fade_points = self.outlines[index][i][fade[0]:] + self.outlines[index][i][:fade[1]]
                    # revers direction
                    else:
                        if fade[0] > fade[1]:
                            fade_points = self.outlines[index][i][fade[1]:fade[0]]
                        else:
                            fade_points = self.outlines[index][i][fade[1]:] + self.outlines[index][i][:fade[0]]

                    points = np.array(fade_points, dtype=np.int32)
                    # Draw lines between the points
                    for p_index in range(len(points)-1):
                        pt1 = points[p_index]
                        pt2 = points[p_index + 1]
                        cv2.line(self.fade_array, tuple(pt1), tuple(pt2), color=data[6][i]+1, thickness=1)

            # delete fade lines that are not needed
            mask = self.fade_array == self.poly_array
            self.fade_array[mask == False] = 0

            # store data in variable
            self.converted_data.update({f"{index}": [copy.deepcopy(self.poly_array), copy.deepcopy(self.fade_array)]})

        # return data
        return self.converted_data[f"{index}"]

    # calculate polygon outline
    def calc_outline(self, data):
        # ready up for bezier calculation
        points = [data[-1]] + data + data[0:3]
        polygon_data = []

        for i in range(len(points) - 4):
            # first point
            vector_points = [points[i + 1][0]]
            if not points[i][1]:
                vector_points.append(self.__get_vector_points(points[i][0], points[i + 1][0], points[i + 2][0])[1])
            # second point
            if not points[i + 1][1]:
                vector_points.append(self.__get_vector_points(points[i + 1][0], points[i + 2][0], points[i + 3][0])[0])
            vector_points.append(points[i + 2][0])

            # add bezier points to poly list
            for pos in self.__calc_bezier(vector_points):
                polygon_data.append(pos)

        return polygon_data

    # get bezier vector points
    @staticmethod
    def __get_vector_points(p1: (int, int), p2: (int, int), p3: (int, int)) -> [(int, int), (int, int)]:
        # calculate delta x/y
        dx, dy = p3[0] - p1[0], p3[1] - p1[1]
        # calculate distances
        p13_dis = sqrt((p3[0] - p1[0]) ** 2 + (p3[1] - p1[1]) ** 2)
        p12_dis = sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        p23_dis = sqrt((p3[0] - p2[0]) ** 2 + (p3[1] - p2[1]) ** 2)

        # return vector points
        if abs(dx) >= abs(dy):
            return (p2[0] - p13_dis / dx * (p12_dis / 3), p2[1] - p13_dis / dx * (p12_dis / 3) * (dy / dx)), \
                   (p2[0] + p13_dis / dx * (p23_dis / 3), p2[1] + p13_dis / dx * (p23_dis / 3) * (dy / dx))
        else:
            return (p2[0] - p13_dis / dy * (p12_dis / 3) * (dx / dy), p2[1] - p13_dis / dy * (p12_dis / 3)), \
                   (p2[0] + p13_dis / dy * (p23_dis / 3) * (dx / dy), p2[1] + p13_dis / dy * (p23_dis / 3))

    # calculate bezier curve
    @staticmethod
    def __calc_bezier(points: list[tuple[int, int]]) -> list[(int, int)]:
        res = round(sqrt((points[-1][0] - points[0][0]) ** 2 + (points[-1][1] - points[0][1]) ** 2))
        n = len(points) - 1
        curve_points = []
        for i in range(res):
            t = i / (res - 1) if res - 1 > 0 else 1
            point = [0, 0]
            for j in range(n + 1):
                cof = comb(n, j) * t ** j * (1 - t) ** (n - j)
                point[0] += cof * points[j][0]
                point[1] += cof * points[j][1]
            curve_points.append(tuple(point))
        return curve_points

