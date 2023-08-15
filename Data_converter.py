import copy
import csv
import ast
import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
from math import *


class Data_converter(object):
    def __init__(self, grid_size: tuple[int, int], box_size: float):
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
            real_rows = [row for row in reader if row]

        # load data
        with open("Data_set/Procedural_Dataset.csv", "r") as csv_file:
            reader = csv.reader(csv_file)
            procedural_rows = [row for i, row in enumerate(reader) if row]

        # convert data
        self.data = [
            [
                row[0],
                float(row[1]),
                ast.literal_eval(row[2]),
                ast.literal_eval(row[3]),
                ast.literal_eval(row[4]),
                ast.literal_eval(row[5]),
                ast.literal_eval(row[6]),
                ast.literal_eval(row[7])
            ]
            for row in real_rows
        ]
        # convert data
        self.procedural_data = [
            [
                row[0],
                float(row[1]),
                ast.literal_eval(row[2]),
                ast.literal_eval(row[3]),
                ast.literal_eval(row[4]),
                ast.literal_eval(row[5]),
                ast.literal_eval(row[6]),
                ast.literal_eval(row[7])
            ]
            for row in procedural_rows
        ]
        self.outlines = [[] for _ in self.data]
        self.procedural_outlines = [[] for _ in self.procedural_data]

        # numpy arrays
        self.color_array = np.zeros((self.GRID_SIZE[1], self.GRID_SIZE[0]), dtype=np.int32)
        
        # outline offsets
        self.outline_curve_points = []
        self.outline_curve_data = []
        self.offset = 35

        # converted data dict
        self.converted_data = {}
        self.procedural_converted_data = {}

    # convert all data
    def convert_all(self, only_par: int = None):
        # progress bar
        print(f"Convert all real holes:")
        print("[{}] {}%".format("." * 20, 0), end="", flush=True)

        # convert data
        for index, data in enumerate(self.data):
            if only_par is None:
                self.convert(data=data)
            else:
                folder_path = 'D:/Ondrive/OneDrive - Venusnet/Dokumente/2. Schule/Maturarbeit/Golf_course_IMGs'
                file_names = os.listdir(folder_path)

                for file in file_names:
                    if file.count(data[0]) and int(file.split("-")[2].split(".")[0]) == only_par:
                        self.convert(data=data)

            # update progress bar
            print("\r", end="")
            print(
                "[{}{}] {}%".format(
                    "=" * floor(index / (len(self.data) - 1) * 20),
                    "." * (20 - floor(index / (len(self.data) - 1) * 20)),
                    index / (len(self.data) - 1) * 100),
                end="", flush=True
            )

        print("\r", end="")
        print("[----- Complete -----] 100%\n", end="", flush=True)
        print(f"{len(list(self.converted_data.values()))} real holes converted!")

        # return data
        return list(self.converted_data.values())

    # convert all procedural data
    def convert_all_procedural(self):
        # progress bar
        print(f"Convert all procedural holes:")
        print("[{}] {}%".format("." * 20, 0), end="", flush=True)

        # convert data
        for index, data in enumerate(self.procedural_data):
            self.convert_procedural(data=data)

            # update progress bar
            print("\r", end="")
            print(
                "[{}{}] {}%".format(
                    "=" * floor(index / (len(self.procedural_data) - 1) * 20),
                    "." * (20 - floor(index / (len(self.procedural_data) - 1) * 20)),
                    index / (len(self.procedural_data) - 1) * 100),
                end="", flush=True
            )

        print("\r", end="")
        print("[----- Complete -----] 100%\n", end="", flush=True)
        print(f"{len(list(self.converted_data.values()))} procedural holes converted!")

        # return data
        return list(self.procedural_converted_data.values())

    # convert one data set
    def convert(self, data=None, index: int = None):
        assert data is not None or index is not None, "No data specified set an index or hand over data"
        self.color_array *= 0

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
                cv2.fillPoly(self.color_array, [points], color=data[5][i] + 1)

            # calculate outline mask
            points = np.array(self.calc_hole_outline(data, delta_x, delta_y), dtype=np.int32)
            points = points.reshape((-1, 1, 2))
            # create mask array
            mask = np.zeros_like(self.color_array)
            # draw polygon
            cv2.fillPoly(mask, [points], color=1)

            # apply outline mask
            self.color_array = np.where(mask == 1, self.color_array, 0)

            # store data in variable
            self.converted_data.update({f"{index}": copy.deepcopy(self.color_array)})

        # return data
        return self.converted_data[f"{index}"]

    # convert one data set
    def convert_procedural(self, data=None, index: int = None):
        assert data is not None or index is not None, "No data specified set an index or hand over data"
        self.color_array *= 0

        # convert index to data
        if data is None and index is not None:
            data = self.procedural_data[index]
        # set index
        if data is not None:
            index = self.procedural_data.index(data)

        # only convert data if it hadn't been converted yet
        if f"{index}" not in self.procedural_converted_data:
            for d_index, d in enumerate(data[4]):
                # calculate outline
                self.procedural_outlines[index].append(self.calc_outline(d))

            # center the outlines
            min_x = min([pos[0] for outline in self.procedural_outlines[index] for pos in outline])
            max_x = max([pos[0] for outline in self.procedural_outlines[index] for pos in outline])
            min_y = min([pos[1] for outline in self.procedural_outlines[index] for pos in outline])
            max_y = max([pos[1] for outline in self.procedural_outlines[index] for pos in outline])

            # delta x/y
            delta_x = - ((max_x - min_x) / 2 + min_x)
            delta_y = - ((max_y - min_y) / 2 + min_y)

            # calculate offset
            for i, outline in enumerate(self.procedural_outlines[index]):
                self.procedural_outlines[index][i] = [[pos[0] + delta_x, pos[1] + delta_y] for pos in outline]

                # convert map data to meters
                for p_index, pos in enumerate(self.procedural_outlines[index][i]):
                    # scale outlines
                    self.procedural_outlines[index][i][p_index][0] *= data[1] / self.BOX_SIZE
                    self.procedural_outlines[index][i][p_index][1] *= data[1] / self.BOX_SIZE

                    # translate to canvas center
                    self.procedural_outlines[index][i][p_index][0] += self.GRID_SIZE[0] / 2
                    self.procedural_outlines[index][i][p_index][1] += self.GRID_SIZE[1] / 2

                # convert outline to cv2 format points
                if len(self.procedural_outlines[index][i]) > 0:
                    points = np.array(self.procedural_outlines[index][i], dtype=np.int32)
                    points = points.reshape((-1, 1, 2))
                    # draw polygon
                    cv2.fillPoly(self.color_array, [points], color=data[5][i] + 1)

            # calculate outline mask
            points = np.array(self.calc_hole_outline(data, delta_x, delta_y), dtype=np.int32)
            points = points.reshape((-1, 1, 2))
            # create mask array
            mask = np.zeros_like(self.color_array)
            # draw polygon
            cv2.fillPoly(mask, [points], color=1)

            # apply outline mask
            self.color_array = np.where(mask == 1, self.color_array, 0)

            # store data in variable
            self.procedural_converted_data.update({f"{index}": copy.deepcopy(self.color_array)})

        # return data
        return self.procedural_converted_data[f"{index}"]

    # calculate polygon outline
    def calc_outline(self, data):
        # ready up for bezier calculation
        if len(data) >= 3:
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
        else:
            return []
    
    # calculate curve points
    def calc_hole_outline(self, data, hole_delta_x, hole_delta_y):
        # fill curve points
        self.outline_curve_points = [[0, 0]] + [[0, 0] for _ in range(len(data[6]) * 2)] + [[0, 0]]

        for i, p in enumerate(data[6]):
            # first points
            if i == 0:
                delta_x, delta_y = data[6][i + 1][0] - p[0], data[6][i + 1][1] - p[1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * self.offset * data[7][i] / data[1]) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else self.offset * data[7][i] / data[1]
                self.outline_curve_points[0] = [p[0] - dx, p[1] - dy]
                self.outline_curve_points[2] = [p[0] + dx, p[1] + dy]

                # parallel offset
                dx = - (delta_x * self.offset * data[7][i] / data[1]) / distance
                dy = - (delta_y * - dx) / delta_x if delta_x != 0 else self.offset * data[7][i] / data[1]
                self.outline_curve_points[1] = [p[0] + dx, p[1] + dy]

            # intermediate points
            elif i != len(data[6]) - 1:
                delta_x, delta_y = data[6][i + 1][0] - data[6][i - 1][0], data[6][i + 1][1] - data[6][i - 1][1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * self.offset * data[7][i] / data[1]) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else self.offset * data[7][i] / data[1]
                self.outline_curve_points[i + 2] = [p[0] + dx, p[1] + dy]
                self.outline_curve_points[len(self.outline_curve_points) - i] = [p[0] - dx, p[1] - dy]

            # last points
            else:
                delta_x, delta_y = p[0] - data[6][i - 1][0], p[1] - data[6][i - 1][1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * self.offset * data[7][i] / data[1]) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else self.offset * data[7][i] / data[1]
                self.outline_curve_points[len(data[6]) + 1] = [p[0] + dx, p[1] + dy]
                self.outline_curve_points[len(data[6]) + 3] = [p[0] - dx, p[1] - dy]

                # parallel offset
                dx = - (delta_x * self.offset * data[7][i] / data[1]) / distance
                dy = - (delta_y * - dx) / delta_x if delta_x != 0 else self.offset * data[7][i] / data[1]
                self.outline_curve_points[len(data[6]) + 2] = [p[0] - dx, p[1] - dy]

        # convert points positions
        for p in self.outline_curve_points:
            p[0] = (p[0] + hole_delta_x) * (data[1] / self.BOX_SIZE) + (self.GRID_SIZE[0] / 2)
            p[1] = (p[1] + hole_delta_y) * (data[1] / self.BOX_SIZE) + (self.GRID_SIZE[1] / 2)

        # return bezier outline
        return self.__calc_hole_bezier()

    # calculate polygon outline
    def __calc_hole_bezier(self):
        # ready up for bezier calculation
        points = [self.outline_curve_points[-1]] + self.outline_curve_points + self.outline_curve_points[0:3]
        outline_points = []

        for i in range(len(points) - 4):
            vector_points = [
                points[i + 1],
                self.__get_vector_points(points[i], points[i + 1], points[i + 2])[1],
                self.__get_vector_points(points[i + 1], points[i + 2], points[i + 3])[0],
                points[i + 2]
            ]

            # add bezier points to poly list
            for pos in self.__calc_bezier(vector_points):
                outline_points.append(pos)

        return outline_points

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
            if dx != 0:
                return (p2[0] - p13_dis / dx * (p12_dis / 3), p2[1] - p13_dis / dx * (p12_dis / 3) * (dy / dx)), \
                       (p2[0] + p13_dis / dx * (p23_dis / 3), p2[1] + p13_dis / dx * (p23_dis / 3) * (dy / dx))
            else:
                return (p2[0], p2[1] - p13_dis * (p12_dis / 3)), \
                       (p2[0], p2[1] + p13_dis * (p23_dis / 3))
        else:
            if dy != 0:
                return (p2[0] - p13_dis / dy * (p12_dis / 3) * (dx / dy), p2[1] - p13_dis / dy * (p12_dis / 3)), \
                       (p2[0] + p13_dis / dy * (p23_dis / 3) * (dx / dy), p2[1] + p13_dis / dy * (p23_dis / 3))
            else:
                return (p2[0] - p13_dis * (p12_dis / 3), p2[1]), \
                       (p2[0] + p13_dis * (p23_dis / 3), p2[1])

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

