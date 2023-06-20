import copy
from tkinter import *
from math import *
import random
import csv
import matplotlib.pyplot as plt
import numpy as np
import cv2
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from Advanced_Canvas import Advanced_Lines, Advanced_Polygon


class Golf_Hole_Generator(object):
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.SIZE = [600, 600]
        self.center = [300, 300]

        # colors
        self.colors = np.array([
            [50, 205, 50],
            [104, 155, 64],
            [33, 153, 50],
            [20, 101, 33],
            [17, 76, 25],
            [210, 180, 140],
            [240, 230, 140],
            [17, 48, 25],
            [70, 130, 180],
            [255, 255, 255],
            [128, 128, 128],
            [226, 114, 91]
        ])

        # outline parameters
        self.outline_offset = 35
        self.outline_points = []
        self.outline_points_scale = []
        self.outline_curve_points = []
        self.outline_curve = []
        self.center_outline_curve_points = []

        # green outlines
        self.green_2_curve_points = []

        self.green_5_curve_points = []
        self.green_6_curve_points = []
        self.green_7_curve_points = []

        self.green_12_curve_points = []

        self.green_14_curve_points = []

        # tee outline
        self.tee_outline_curve_points = []
        self.tee_5_curve_points = []

        # bunker outline
        self.bunker_5_curve_points = []

        # water outlines
        self.water_12_curve_points = []

        # path parameters
        self.path = None
        self.path_curve_points = []

        # polygon outlines
        self.polygon_curve_12_points = []

        # polygon parameters
        self.polygon_colors = []
        self.polygon_z_pos = []
        self.polygon_curve_points = []
        self.polygon_curve_points_type = []
        self.polygon_curve = []

        # widgets
        self.outline_widget = Advanced_Lines(self.canvas, [], 1, (0, 0, 0))
        self.polygon_widgets = []

    # par [integer], distance [meter], dog_leg [meter]
    def generate_hole(self, par: int = 4, distance: int = 400, dog_leg: int = 0, visualise: bool = False, seed: int = 1):
        assert distance > 110, f"Distance of Golfhole has to be longer than 110m it is currently {distance}"
        assert 2 < par < 7, f"Par should be between 3 and 6 it is currently {par}"
        assert dog_leg < distance / 2, f"to strong dog leg, dogleg has to be smaller than {distance / 2}"
        
        # set seed
        random.seed(seed)

        # save to csv
        with open("Data_set/Procedural_Dataset.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = [row for row in csv_reader if int(row[0]) == seed]

        if len(rows) == 0:
            # generate
            self.__generate_outline(
                par=par,
                distance=distance,
                dog_leg=dog_leg
            )
            self.__generate_green()
            self.__generate_tee(
                offset_angle=random.randint(-4, 4)
            )
            if random.randint(0, 10) <= 4:
                self.__generate_path(
                    par=par,
                    align_side="left" if random.randint(0, 1) == 0 else "right"
                )
            self.__generate_water(
                stream_count=random.randint(1, 2) if random.randint(0, 1) == 1 else 0,
                lake_count=random.randint(1, 2) if random.randint(0, 3) == 3 else 0,
                distance=distance
            )
            self.__generate_buildings(
                random.randint(1, 2) if random.randint(0, 2) == 0 else 0
            )
            self.__generate_bunker(
                green_bunker_count=random.randint(1, 3),
                fairway_bunker_count=random.randint(1, 4),
                par=par,
                distance=distance
            )
            self.__generate_rough(
                count=random.randint(0, 3),
                distance=distance
            )
            self.__generate_out(1)
            self.__generate_fairway(
                par=par
            )
            self.__generate_trees(
                tree_count=random.randint(0, 20)
            )
            self.__generate_semi_rough()

            # visualise
            if visualise:
                self.__visualise_polygons()
                self.__visualise_outline()

            # save to dataset
            curve_points, curve_colors = self.get_curve_points()
            data = [
                seed,
                1,
                self.outline_points[0],
                self.outline_points[-1],
                curve_points,
                curve_colors,
                self.outline_points,
                self.outline_points_scale
            ]
            with open("Data_set/Procedural_Dataset.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                rows = [row for row in csv_reader]
            with open("Data_set/Procedural_Dataset.csv", "w", newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                rows.append(data)
                csv_writer.writerows(rows)

    def get_curve_points(self):
        # calc indices
        z_values = np.sort(np.unique(self.polygon_z_pos))[::-1]
        indices = []
        for val in z_values:
            indices.append(list(np.where(np.array(self.polygon_z_pos) == val)[0]))

        curve_points = []
        curve_colors = []
        for z_val in indices:
            for i in z_val:
                # calculate polygon outline
                points = [[list(p), t] for p, t in zip(self.polygon_curve_points[i], self.polygon_curve_points_type[i])]
                print(points)
                curve_points.append(points)
                curve_colors.append(self.colors.tolist().index(self.polygon_colors[i].tolist()))

        return curve_points, curve_colors

    # par [integer], distance [meter], dog_leg [meter]
    def __generate_outline(self, par: int, distance: int, dog_leg: int):
        # generate starting and ending point
        self.outline_points.append([0, distance / 2])
        self.outline_points_scale.append(0.5)  
        self.outline_points.append([0, - distance / 2])
        self.outline_points_scale.append(1)  

        scale = random.randint(120, 150) / 100  
        # generate sub points
        for i in range(par - 3):
            # calculate offsets
            x_offset = random.randint(-10, 10) + dog_leg  
            y_offset = random.randint(-20, 20)  
            points_scale = scale * random.randint(95, 105) / 100  
            # save points
            self.outline_points.insert(1 + i, [x_offset, distance / 2 - distance / (par - 2) * (i + 1) + y_offset])
            self.outline_points_scale.insert(1 + i, points_scale)

        # calculate curve
        self.outline_curve_points = self.__calc_outline_curve_points(
            line=False,
            points=self.outline_points,
            points_scale=self.outline_points_scale,
            width=self.outline_offset
        )
        self.center_outline_curve_points = self.__calc_outline_curve_points(
            line=False,
            points=self.outline_points,
            points_scale=self.outline_points_scale,
            width=10
        )
        self.__calc_outline_curve()

    # calculate curve points; line [line or outline], points [list[x, y points]], points_scale [float], width [meter]
    @staticmethod
    def __calc_outline_curve_points(line: bool = False, points: list[list[int, int]] = None, points_scale: list[int] = None, width: int = 5):
        # outline parameters
        if not line:
            curve_points = [[0, 0]] + [[0, 0] for _ in range(len(points) * 2)] + [[0, 0]]
            points_scale = points_scale if points_scale is not None else [1.0 for _ in range(len(points))]
            offset = width
        # line parameters
        else:
            curve_points = [[0, 0] for _ in range(len(points) * 2)]
            points_scale = [1.0 for _ in range(len(points))]
            offset = width / 2

        for i, p in enumerate(points):
            # first points
            if i == 0:
                delta_x, delta_y = points[i + 1][0] - p[0], points[i + 1][1] - p[1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * offset * points_scale[i]) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else offset * points_scale[i]
                curve_points[0] = [p[0] - dx, p[1] - dy]
                curve_points[2 if not line else 1] = [p[0] + dx, p[1] + dy]

                # parallel offset
                if not line:
                    dx = - (delta_x * offset * points_scale[i]) / distance
                    dy = - (delta_y * - dx) / delta_x if delta_x != 0 else offset * points_scale[i]
                    curve_points[1] = [p[0] + dx, p[1] + dy]

            # intermediate points
            elif i != len(points) - 1:
                delta_x, delta_y = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * offset * points_scale[i]) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else offset * points_scale[i]
                curve_points[i + 2 if not line else i + 1] = [p[0] + dx, p[1] + dy]
                curve_points[len(curve_points) - i if not line else len(curve_points) - i] = [p[0] - dx, p[1] - dy]

            # last points
            else:
                delta_x, delta_y = p[0] - points[i - 1][0], p[1] - points[i - 1][1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * offset * points_scale[i]) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else offset * points_scale[i]
                curve_points[len(points) + 1 if not line else len(points)] = [p[0] + dx, p[1] + dy]
                curve_points[len(points) + 3 if not line else len(points) + 1] = [p[0] - dx, p[1] - dy]

                # parallel offset
                if not line:
                    dx = - (delta_x * offset * points_scale[i]) / distance
                    dy = - (delta_y * - dx) / delta_x if delta_x != 0 else offset * points_scale[i]
                    curve_points[len(points) + 2] = [p[0] - dx, p[1] - dy]

        # return  curve points
        return curve_points

    # calculate polygon outline
    def __calc_outline_curve(self):
        self.outline_curve.clear()
        # ready up for bezier calculation
        points = [self.outline_curve_points[-1]] + self.outline_curve_points + self.outline_curve_points[0:3]

        # calc outline
        for i in range(len(points) - 4):
            # ger bezier points
            vector_points = [
                points[i + 1],
                self.__get_vector_points(points[i], points[i + 1], points[i + 2])[1],
                self.__get_vector_points(points[i + 1], points[i + 2], points[i + 3])[0],
                points[i + 2]
            ]

            # add bezier curve to outline list
            for pos in self.__calc_bezier(vector_points):
                self.outline_curve.append(list(pos))

    # visualise outline
    def __visualise_outline(self):
        # calculate offsets
        points = copy.deepcopy(self.outline_curve)
        for p in points:
            p[0] += self.center[0]
            p[1] += self.center[1]

        # visualise
        self.outline_widget.set_pos(points)
        self.outline_widget.draw()

    # generate green
    def __generate_green(self):
        # set parameters
        green_height = random.randint(20, 30)  
        green_width = random.randint(20, 30)  
        resolution = 360 // 10
        noise = self.__generate_noise(random.randint(2, 7), resolution, substeps=random.randint(1, 3))  
        center = self.outline_points[-1]

        # polygon outline
        self.polygon_curve_12_points.append([])

        # add green to polygon list
        self.polygon_z_pos.append(1)
        self.polygon_colors.append(self.colors[0])
        self.polygon_curve.append([])
        self.polygon_curve_points.append([])
        self.polygon_curve_points_type.append([])

        for alpha in range(resolution):
            index = alpha
            alpha *= 360 / resolution
            # calculate hypotenuse
            sub_hyp = alpha / 90 - floor(alpha / 90)
            if floor(alpha / 90) == 0 or floor(alpha / 90) == 2:
                hyp = green_width / 2 * sub_hyp + green_height / 2 * (1 - sub_hyp)
            else:
                hyp = green_width / 2 * (1 - sub_hyp) + green_height / 2 * sub_hyp

            # calculate green outline points pos
            x = sin(radians(alpha)) * (hyp + noise[index]) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index]) + center[1]
            self.polygon_curve_points[-1].append([x, y])
            self.polygon_curve_points_type[-1].append(False)

            # green 2 outline -> 2m green outline for the fairway
            x = sin(radians(alpha)) * (hyp + noise[index] + 2) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index] + 2) + center[1]
            self.green_2_curve_points.append([x, y])

            # green 5 outline -> 5m green outline for the bunkers
            x = sin(radians(alpha)) * (hyp + noise[index] + 5) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index] + 5) + center[1]
            self.green_5_curve_points.append([x, y])

            # green 6 outline -> 6m green outline for the bunkers
            x = sin(radians(alpha)) * (hyp + noise[index] + 6) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index] + 6) + center[1]
            self.green_6_curve_points.append([x, y])

            # green 7 outline -> 7m green outline for the bunkers
            x = sin(radians(alpha)) * (hyp + noise[index] + 7) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index] + 7) + center[1]
            self.green_7_curve_points.append([x, y])

            # green 12 outline -> 12m green outline
            x = sin(radians(alpha)) * (hyp + noise[index] + 12) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index] + 12) + center[1]
            self.green_12_curve_points.append([x, y])

            # polygon outline
            self.polygon_curve_12_points[-1].append([x, y])

            # green 14 outline -> 14m green outline for water
            x = sin(radians(alpha)) * (hyp + noise[index] + 14) + center[0]
            y = cos(radians(alpha)) * (hyp + noise[index] + 14) + center[1]
            self.green_14_curve_points.append([x, y])

    # offset_angle [degrees], resolution [steps]
    def __generate_tee(self, offset_angle: int, resolution: int = 10):
        # parameters
        corner_radius = random.randint(5, 10)  # unit is degrees -> from seed
        rotation = atan2(
            self.outline_points[0][0] - self.outline_points[1][0],
            self.outline_points[0][1] - self.outline_points[1][1]
        ) + radians(offset_angle)
        tee_width = random.randint(5, 7)

        # round white tee
        if random.randint(0, 3) <= 2:  
            # set tee parameters
            w_center = [self.outline_points[0][0], self.outline_points[0][1]]
            w_radius = floor(tee_width / 2) + random.randint(0, 2)  

            # height
            w_height = w_radius * 2

            # calculate white tee curve points
            w_tee_curve_points, w_tee_curve_points_type = self.__generate_circular_curve_points(w_center, w_radius,
                                                                                                resolution)

            # calculate white tee curve 5m outline points
            self.tee_5_curve_points.append(self.__generate_circular_curve_points(w_center, w_radius + 5, resolution)[0])

            # polygon outline
            self.polygon_curve_12_points.append(
                self.__generate_circular_curve_points(w_center, w_radius + 12, resolution)[0])
        # rectangular white tee
        else:
            # set tee parameters
            w_center = [self.outline_points[0][0], self.outline_points[0][1]]
            w_height = tee_width + random.randint(-1, 1)  
            w_width = random.randint(8, 12)  

            # calculate white tee curve points
            w_tee_curve_points, w_tee_curve_points_type = self.__generate_rectangular_tee(
                w_center,
                rotation,
                w_height,
                w_width,
                corner_radius,
                resolution * 3
            )

            # calculate white tee curve 5m outline points
            self.tee_5_curve_points.append(
                self.__generate_rectangular_tee(
                    w_center,
                    rotation,
                    w_height + 10,
                    w_width + 10,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # polygon outline
            self.polygon_curve_12_points.append(
                self.__generate_rectangular_tee(
                    w_center,
                    rotation,
                    w_height + 24,
                    w_width + 24,
                    corner_radius,
                    resolution * 3
                )[0]
            )

        # create new polygon
        self.polygon_z_pos.append(1)
        self.polygon_colors.append(self.colors[1])
        self.polygon_curve.append([])
        self.polygon_curve_points.append(w_tee_curve_points)
        self.polygon_curve_points_type.append(w_tee_curve_points_type)

        # merge yellow and blue tee
        if random.randint(0, 7) <= 5:
            b_height = yb_height = random.randint(30, 35)  
            yb_width = tee_width + random.randint(-1, 1)  
            w_yb_dis = random.randint(5, 15)  
            b_center = yb_center = [
                w_center[0] - sin(rotation) * (yb_height / 2 + w_yb_dis + w_height / 2) + random.randint(-5, 5),
                
                w_center[1] - cos(rotation) * (yb_height / 2 + w_yb_dis + w_height / 2)
            ]

            # calculate white tee curve points
            yb_tee_curve_points, yb_tee_curve_points_type = self.__generate_rectangular_tee(
                yb_center,
                rotation,
                yb_height,
                yb_width,
                corner_radius,
                resolution * 3
            )

            # calculate white tee curve 5m outline points
            self.tee_5_curve_points.append(
                self.__generate_rectangular_tee(
                    yb_center,
                    rotation,
                    yb_height + 10,
                    yb_width + 10,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # polygon outline
            self.polygon_curve_12_points.append(
                self.__generate_rectangular_tee(
                    yb_center,
                    rotation,
                    yb_height + 24,
                    yb_width + 24,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # create new polygon
            self.polygon_z_pos.append(1)
            self.polygon_colors.append(self.colors[1])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(yb_tee_curve_points)
            self.polygon_curve_points_type.append(yb_tee_curve_points_type)
        # yellow and blue as unique tees
        else:
            # yellow tee
            y_height = random.randint(18, 22)  
            y_width = tee_width + random.randint(-1, 1)  
            w_y_dis = random.randint(5, 15)  
            y_center = [
                w_center[0] - sin(rotation) * (y_height / 2 + w_y_dis + w_height / 2) + random.randint(-5, 5),
                
                w_center[1] - cos(rotation) * (y_height / 2 + w_y_dis + w_height / 2)
            ]

            # calculate white tee curve points
            y_tee_curve_points, y_tee_curve_points_type = self.__generate_rectangular_tee(
                y_center,
                rotation,
                y_height,
                y_width,
                corner_radius,
                resolution * 3
            )

            # calculate white tee curve 5m outline points
            self.tee_5_curve_points.append(
                self.__generate_rectangular_tee(
                    y_center,
                    rotation,
                    y_height + 10,
                    y_width + 10,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # polygon outline
            self.polygon_curve_12_points.append(
                self.__generate_rectangular_tee(
                    y_center,
                    rotation,
                    y_height + 24,
                    y_width + 24,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # create new polygon
            self.polygon_z_pos.append(1)
            self.polygon_colors.append(self.colors[1])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(y_tee_curve_points)
            self.polygon_curve_points_type.append(y_tee_curve_points_type)

            # blue
            b_height = random.randint(18, 22)  
            b_width = tee_width + random.randint(-1, 1)  
            y_b_dis = random.randint(5, 15)  
            b_center = [
                y_center[0] - sin(rotation) * (b_height / 2 + y_b_dis + y_height / 2) + random.randint(-5, 5),
                
                y_center[1] - cos(rotation) * (b_height / 2 + y_b_dis + y_height / 2)
            ]

            # calculate white tee curve points
            b_tee_curve_points, b_tee_curve_points_type = self.__generate_rectangular_tee(
                b_center,
                rotation,
                b_height,
                b_width,
                corner_radius,
                resolution * 3
            )

            # calculate white tee curve 5m outline points
            self.tee_5_curve_points.append(
                self.__generate_rectangular_tee(
                    b_center,
                    rotation,
                    b_height + 10,
                    b_width + 10,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # polygon outline
            self.polygon_curve_12_points.append(
                self.__generate_rectangular_tee(
                    b_center,
                    rotation,
                    b_height + 24,
                    b_width + 24,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # create new polygon
            self.polygon_z_pos.append(1)
            self.polygon_colors.append(self.colors[1])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(b_tee_curve_points)
            self.polygon_curve_points_type.append(b_tee_curve_points_type)

        # round red tee
        if random.randint(0, 3) <= 2:  
            # set tee parameters
            r_radius = floor(tee_width / 2) + random.randint(0, 2)  
            b_r_dis = random.randint(5, 15)  
            r_center = [
                b_center[0] - sin(rotation) * (r_radius + b_r_dis + b_height / 2) + random.randint(-5, 5),
                
                b_center[1] - cos(rotation) * (r_radius + b_r_dis + b_height / 2)
            ]
            r_height = r_radius * 2

            # calculate red tee curve points
            r_tee_curve_points, r_tee_curve_points_type = self.__generate_circular_curve_points(r_center, r_radius,
                                                                                                resolution)

            # calculate red tee curve 5m outline points
            self.tee_5_curve_points.append(self.__generate_circular_curve_points(r_center, r_radius + 5, resolution)[0])

            # polygon outline
            self.polygon_curve_12_points.append(
                self.__generate_circular_curve_points(r_center, r_radius + 12, resolution)[0])
        # rectangular red tee
        else:
            # set tee parameters
            r_height = tee_width + random.randint(-1, 1)  
            r_width = random.randint(8, 12)  
            b_r_dis = random.randint(5, 15)  
            r_center = [
                b_center[0] - sin(rotation) * (r_height / 2 + b_r_dis + b_height / 2) + random.randint(-5, 5),
                
                b_center[1] - cos(rotation) * (r_height / 2 + b_r_dis + b_height / 2)
            ]

            # calculate red tee curve points
            r_tee_curve_points, r_tee_curve_points_type = self.__generate_rectangular_tee(
                r_center,
                rotation,
                r_height,
                r_width,
                corner_radius,
                resolution * 3
            )

            # calculate red tee curve 5m outline points
            self.tee_5_curve_points.append(
                self.__generate_rectangular_tee(
                    r_center,
                    rotation,
                    r_height + 10,
                    r_width + 10,
                    corner_radius,
                    resolution * 3
                )[0]
            )

            # calculate red tee curve 5m outline points
            self.polygon_curve_12_points.append(
                self.__generate_rectangular_tee(
                    r_center,
                    rotation,
                    r_height + 24,
                    r_width + 24,
                    corner_radius,
                    resolution * 3
                )[0]
            )

        # tee outline
        curve_points = self.__calc_outline_curve_points(
            line=False,
            points=[w_center, r_center],
            points_scale=[1, 1],
            width=max(w_height, r_height) + 2
        )
        self.tee_outline_curve_points = self.__re_mesh_polygon(curve_points, [False for _ in curve_points], "auto")

        # create new polygon
        self.polygon_z_pos.append(1)
        self.polygon_colors.append(self.colors[1])
        self.polygon_curve.append([])
        self.polygon_curve_points.append(r_tee_curve_points)
        self.polygon_curve_points_type.append(r_tee_curve_points_type)

    # center [x, y point], rotation [degrees], height [meter], width [meter], corner_radius [degrees], resolution [integer]
    @staticmethod
    def __generate_rectangular_tee(center: list[int, int], rotation: float, height: int, width: int, corner_radius: int,
                                   resolution: int):
        tee_curve_points = []
        tee_curve_points_type = []

        # calculate corner curve parameters
        corner_angle = degrees(atan2(width, height))
        wc_start_hyp = (height / 2) / cos(radians(corner_angle - corner_radius))
        wc_end_hyp = (width / 2) / sin(radians(corner_angle + corner_radius))
        wc_ratio = (wc_end_hyp - wc_start_hyp) / (corner_radius * 2)

        # calculate curve points
        for alpha in range(resolution):
            alpha *= 360 / resolution
            # calculate hypotenuse
            sub_hyp = alpha / 90 - floor(alpha / 90)

            if floor(alpha / 90) == 0 or floor(alpha / 90) == 2:
                if sub_hyp * 90 + corner_radius < corner_angle:
                    hyp = (height / 2) / cos(radians(sub_hyp * 90))
                elif sub_hyp * 90 - corner_radius > corner_angle:
                    hyp = (width / 2) / sin(radians(sub_hyp * 90))
                else:
                    hyp = wc_start_hyp + wc_ratio * ((sub_hyp * 90) - (corner_angle - corner_radius))

            else:
                if (1 - sub_hyp) * 90 + corner_radius < corner_angle:
                    hyp = (height / 2) / cos(radians((1 - sub_hyp) * 90))
                elif (1 - sub_hyp) * 90 - corner_radius > corner_angle:
                    hyp = (width / 2) / sin(radians((1 - sub_hyp) * 90))
                else:
                    hyp = wc_start_hyp + wc_ratio * (((1 - sub_hyp) * 90) - (corner_angle - corner_radius))

            # calculate green outline points pos
            x = sin(radians(alpha) + rotation) * hyp + center[0]
            y = cos(radians(alpha) + rotation) * hyp + center[1]
            tee_curve_points.append([x, y])
            tee_curve_points_type.append(False)

        return tee_curve_points, tee_curve_points_type

    # center [x, y point], resolution [integer]
    @staticmethod
    def __generate_circular_curve_points(center: list[int, int], radius: int, resolution: int,
                                         noise: list[float] = None):
        curve_points = []
        curve_points_type = []

        # set noise if it is None
        if noise is None:
            noise = [1 for _ in range(resolution)]

        # create curve points
        for i in range(resolution):
            # calculate circle position
            x_pos = sin(radians(360 / resolution * i)) * (radius + noise[i]) + center[0]
            y_pos = cos(radians(360 / resolution * i)) * (radius + noise[i]) + center[1]

            curve_points.append([x_pos, y_pos])
            curve_points_type.append(False)

        return curve_points, curve_points_type

    # par [integer], align_side ["left" or "right"]
    def __generate_path(self, par: int, align_side: str = "left"):
        path_offset = random.randint(0, 10)  
        self.path = align_side

        # get line points
        if align_side == "left":
            points = self.outline_curve_points[2 + par:] + [self.outline_curve_points[0]]
            points = [[p[0] + path_offset, p[1]] for p in points]
            # move out starting & ending points
            points[0][0] -= path_offset
            points[-1][0] -= path_offset
        else:
            points = self.outline_curve_points[2:1 + par]
            points = [[p[0] - path_offset, p[1]] for p in points]
            # move out starting & ending points
            points[0][0] += path_offset
            points[-1][0] += path_offset

        # expand starting point
        points[0] = self.__expand_point(points[0], points[1], 30)
        points[-1] = self.__expand_point(points[-1], points[-2], 30)

        # calculate sub points
        curve_points = self.__calc_outline_curve_points(line=True, points=points, width=4)
        curve_points_type = [True for _ in curve_points]

        # polygon outline
        self.polygon_curve_12_points.append(self.__calc_outline_curve_points(line=True, points=points, width=4 + 24))

        # add curve points to class list
        self.path_curve_points.append(curve_points)

        # create new polygon
        self.polygon_z_pos.insert(0, -1)
        self.polygon_colors.insert(0, self.colors[10])
        self.polygon_curve.insert(0, [])
        self.polygon_curve_points.insert(0, curve_points)
        self.polygon_curve_points_type.insert(0, curve_points_type)

    # stream_count [count/integer], lake_count [count/integer], distance [meter]
    def __generate_water(self, stream_count: int, lake_count: int, distance: int):
        # generate stram
        if distance < 100:
            if distance < 200:
                stream_count = stream_count if stream_count == 0 else 1
            stream_outline_curve_points = []
            for i in range(stream_count):
                # set parameters
                stream_range = [
                    150 if distance > 250 else 80,
                    distance - 100 if distance > 250 else distance - 30
                ]
                y_pos = self.outline_points[0][1] - random.randint(stream_range[0], stream_range[1])  
                left_y_offset = random.randint(-20, 20)  
                right_y_offset = random.randint(-20, 20)  
                res = random.randint(10, 15)  
                noise = self.__generate_noise(20, res, substeps=random.randint(2, 5))  
                width = random.randint(3, 8)  

                # calculate pos
                y_negation = False
                while True:
                    left_y = left_y_offset + y_pos
                    right_y = right_y_offset + y_pos
                    # calculate
                    for index, p in enumerate(self.outline_points):
                        if p[1] < y_pos:
                            start_p = p
                            end_p = self.outline_points[index - 1]
                            x_pos = start_p[0] + (end_p[0] - start_p[0]) / (end_p[1] - start_p[1]) * (y_pos - start_p[1])
                            break
                    else:
                        x_pos = self.outline_points[-1][0]

                    # calculate points
                    points = [
                        [x_pos - 100 + (200 / res * i), right_y + (right_y - left_y) / res * i + noise[i]]
                        for i in range(res)
                    ]

                    # create curve points list
                    curve_points = self.__calc_outline_curve_points(
                        line=True,
                        points=points,
                        points_scale=[1 for _ in range(res)],
                        width=width
                    )
                    # create 60m outline curve points list
                    curve_60_points = self.__calc_outline_curve_points(
                        line=True,
                        points=points,
                        points_scale=[1 for _ in range(res)],
                        width=width + 60
                    )
                    # create 12m outline curve points list
                    curve_12_points = self.__calc_outline_curve_points(
                        line=True,
                        points=points,
                        points_scale=[1 for _ in range(res)],
                        width=width + 20
                    )
                    curve_points_type = [False for _ in curve_points]

                    # intersection test
                    for stram_poly in stream_outline_curve_points:
                        # check for other building intersection
                        if Polygon(curve_60_points).intersects(Polygon(stram_poly)):
                            if y_negation:
                                y_pos -= 15
                            elif y_pos + 15 < self.outline_points[0][1] - 150:
                                y_pos += 15
                            else:
                                y_negation = True
                                y_pos -= 15
                            break
                    else:
                        stream_outline_curve_points.append(curve_60_points)
                        self.water_12_curve_points.append(curve_12_points)

                        # polygon outline
                        self.polygon_curve_12_points.append(curve_12_points)
                        break

                # generate bridge
                if self.path is None:
                    # create curve points list
                    center_line = self.__calc_outline_curve_points(
                        line=True,
                        points=points,
                        points_scale=[1 for _ in range(res)],
                        width=1
                    )

                    # calculate bridge position
                    path_x_pos = x_pos
                    y_index = np.abs(np.array(center_line)[:, 0] - path_x_pos).argmin()
                    path_y_pos = center_line[y_index][1]

                    # calculate angle
                    if center_line[y_index][0] > path_x_pos:
                        dx = center_line[y_index][0] - center_line[y_index + 1][0]
                        dy = center_line[y_index][1] - center_line[y_index + 1][1]
                        angle = atan2(dx, dy) + radians(90)
                    else:
                        dx = center_line[y_index - 1][0] - center_line[y_index][0]
                        dy = center_line[y_index - 1][1] - center_line[y_index][1]
                        angle = atan2(dx, dy) + radians(90)

                    path_curve_points = self.__calc_rectangle_cords([path_x_pos, path_y_pos], 4, width * 2 + 4, angle)
                    self.polygon_curve_12_points.append(
                        self.__calc_rectangle_cords([path_x_pos, path_y_pos], 4 + 12, width * 2 + 12, angle)
                    )

                    # create new polygon
                    self.polygon_z_pos.append(-1)
                    self.polygon_colors.append(self.colors[10])
                    self.polygon_curve.append([])
                    self.polygon_curve_points.append(path_curve_points)
                    self.polygon_curve_points_type.append([True for _ in path_curve_points])

                # create new polygon
                self.polygon_z_pos.insert(0, -1)
                self.polygon_colors.insert(0, self.colors[8])
                self.polygon_curve.insert(0, [])
                self.polygon_curve_points.insert(0, curve_points)
                self.polygon_curve_points_type.insert(0, curve_points_type)

        # calculate lake ring -> where lakes will be placed
        lake_ring_points = self.__calc_outline_curve_points(
            line=False,
            points=self.outline_points,
            points_scale=self.outline_points_scale,
            width=self.outline_offset - 5
        )
        lake_ring = self.__calc_polygon_outline(
            None,
            lake_ring_points,
            [False for _ in lake_ring_points]
        )
        # generate lake
        for i in range(lake_count):
            # remove the points on the path side
            if self.path == "left":
                lake_ring = [p for p in lake_ring if p[0] > 0]
            elif self.path == "right":
                lake_ring = [p for p in lake_ring if p[0] < 0]

            # set parameters
            y_pos = self.outline_points[0][1] - random.randint(50, distance)  
            height = random.randint(35, 55) * 2  
            width = random.randint(18, 26) * 2  
            noise = self.__generate_noise(20, 8, substeps=random.randint(2, 3))  
            x_pos = lake_ring[np.abs(np.array(lake_ring)[:, 1] - y_pos).argmin()][0]
            resolution = 8

            curve_points = []
            curve_points_type = []
            self.water_12_curve_points.append([])
            self.polygon_curve_12_points.append([])
            # calculate lake curve points
            for alpha in range(resolution):
                index = alpha
                alpha *= 360 / resolution
                # calculate hypotenuse
                sub_hyp = alpha / 90 - floor(alpha / 90)
                if floor(alpha / 90) == 0 or floor(alpha / 90) == 2:
                    hyp = width / 2 * sub_hyp + height / 2 * (1 - sub_hyp)
                else:
                    hyp = width / 2 * (1 - sub_hyp) + height / 2 * sub_hyp

                # calculate lake curve points pos
                x = sin(radians(alpha)) * (hyp + noise[index]) + x_pos
                y = cos(radians(alpha)) * (hyp + noise[index]) + y_pos
                curve_points.append([x, y])
                curve_points_type.append(False)

                # calculate green outline points pos
                x = sin(radians(alpha)) * (hyp + 12 + noise[index]) + x_pos
                y = cos(radians(alpha)) * (hyp + 12 + noise[index]) + y_pos
                self.water_12_curve_points[-1].append([x, y])

                # polygon outline
                self.polygon_curve_12_points[-1].append([x, y])

            # lake keep out zone
            lake_keep_out_zone = self.__calc_outline_curve_points(
                line=False,
                points=self.outline_points,
                points_scale=self.outline_points_scale,
                width=self.outline_offset - 30
            )

            # cut out different polygons
            for cut_poly in [self.green_14_curve_points] + [self.tee_outline_curve_points] + [self.center_outline_curve_points]:
                # calculate intersection points
                curve_points = self.__cut_polygon_from_polygon(curve_points, cut_poly)[0]

            curve_points = self.__cut_polygon_from_polygon(curve_points, lake_keep_out_zone)[0]
            curve_points = self.__re_mesh_polygon(curve_points, [False for _ in curve_points], "auto")

            curve_points_type = [False for _ in curve_points]

            # create new polygon
            self.polygon_z_pos.insert(0, -1)
            self.polygon_colors.insert(0, self.colors[8])
            self.polygon_curve.insert(0, [])
            self.polygon_curve_points.insert(0, curve_points)
            self.polygon_curve_points_type.insert(0, curve_points_type)

    # count [integer/count]
    def __generate_buildings(self, count: int):
        building_polygons = []

        # create buildings
        for i in range(count):
            location = random.randint(0, len(self.outline_curve) - 1)  

            # define variables
            center_offset = [random.randint(-5, 5), random.randint(-5, 5)]  
            height = random.randint(10, 25)  
            width = random.randint(10, 25)  
            rotation = radians(random.randint(0, 90))  

            while True:
                # normalize location
                if location > len(self.outline_curve) - 1:
                    location -= len(self.outline_curve) - 1

                center = [
                    self.outline_curve[location][0] + center_offset[0],
                    self.outline_curve[location][1] + center_offset[1]
                ]

                # calculate rectangle coordinates
                curve_points = self.__calc_rectangle_cords(center, width, height, rotation)
                curve_12_points = self.__calc_rectangle_cords(center, width + 24, height + 24, rotation)

                # intersection test
                for build_poly in building_polygons:
                    # check for other building intersection
                    if Polygon(curve_points).intersects(Polygon(build_poly)):
                        location += 5
                        break
                else:
                    # check for green intersection
                    if Polygon(curve_points).intersects(Polygon(self.green_12_curve_points)):
                        location += 5
                    else:
                        # check for stream intersection
                        for stream_poly in self.water_12_curve_points:
                            if Polygon(curve_points).intersects((Polygon(stream_poly))):
                                location += 5
                                break
                        else:
                            # check for tee intersection
                            for tee_poly in self.tee_5_curve_points:
                                # check for tee intersection
                                if Polygon(curve_points).intersects(Polygon(tee_poly)):
                                    location += 5
                                    break
                            # no intersections leave while loop
                            else:
                                # polygon outline
                                self.polygon_curve_12_points.append(curve_12_points)
                                break

            # check if they intersect with the path
            for path_curve_points in self.path_curve_points:
                if len(path_curve_points) > 0 and Polygon(path_curve_points).intersects(Polygon(curve_points)):
                    path_curve = self.__calc_rectangle_cords(center, width + 8, height + 8, rotation)
                    path_12_curve = self.__calc_rectangle_cords(center, width + 8 + 24, height + 8 + 24, rotation)

                    # check for green intersection
                    if not Polygon(path_curve).intersects(Polygon(self.green_12_curve_points)):
                        # create new polygon
                        self.polygon_z_pos.append(-1)
                        self.polygon_colors.append(self.colors[10])
                        self.polygon_curve.append([])
                        self.polygon_curve_points.append(path_curve)
                        self.polygon_curve_points_type.append([True, True, True, True])

                        # polygon outline
                        self.polygon_curve_12_points.append(path_12_curve)

                        self.path_curve_points.append(path_curve)
                        break

            # create new polygon
            self.polygon_z_pos.append(-1)
            self.polygon_colors.append(self.colors[11])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(curve_points)
            self.polygon_curve_points_type.append([True, True, True, True])

            building_polygons.append(curve_points)

    # green_bunker_count [count/integer], fairway_bunker_count [count/integer], distance [meter]
    def __generate_bunker(self, green_bunker_count: int = 2, fairway_bunker_count: int = 1, par: int = 4, distance: int = 0):
        green_bunker_curve_points = []
        # green bunkers
        for i in range(green_bunker_count):
            # worm bunker
            if random.randint(0, 3) <= 2:
                # set parameters
                start_index = random.randint(0, len(self.green_7_curve_points))
                length = random.randint(2, 5)  
                start_line = random.randint(0, 1) + 5  
                end_line = random.randint(0, 1) + 5  
                width = -3 + min(end_line, start_line)

                while True:
                    # calculate points
                    start_point = self.__get_green_outline_curve_point(start_line, start_index)
                    center_point = self.__get_green_outline_curve_point(7, start_index + floor(length / 2))
                    end_point = self.__get_green_outline_curve_point(end_line, start_index + length)

                    # calculate curve points
                    curve_points = self.generate_bunker_outline(
                        line_points=[start_point, center_point, end_point],
                        radius=width
                    )
                    # 2m curve points outline
                    curve_5_points = self.generate_bunker_outline(
                        line_points=[start_point, center_point, end_point],
                        radius=width + 2
                    )

                    # check for intersections
                    for bunker_poly in green_bunker_curve_points:
                        if Polygon(curve_5_points).intersects(Polygon(bunker_poly)):
                            start_index += 1
                            break
                    else:
                        green_bunker_curve_points.append(curve_5_points)
                        break

                # curve points type
                curve_points_type = [False for _ in curve_points]
            # round bunker
            else:
                # set parameters
                index = random.randint(0, len(self.green_7_curve_points))
                list_num = random.randint(0, 2) + 5  
                width = -3 + list_num

                while True:
                    # create/update center
                    center = self.__get_green_outline_curve_point(list_num, index)

                    curve_points, curve_points_type = self.__generate_circular_curve_points(
                        center=center,
                        radius=width,
                        resolution=10
                    )

                    curve_5_points, _ = self.__generate_circular_curve_points(
                        center=center,
                        radius=width + 2,
                        resolution=10
                    )

                    # check for intersections
                    for bunker_poly in green_bunker_curve_points:
                        if Polygon(curve_5_points).intersects(Polygon(bunker_poly)):
                            index += 1
                            break
                    else:
                        green_bunker_curve_points.append(curve_5_points)
                        break

            # create new polygon
            self.polygon_z_pos.append(1)
            self.polygon_colors.append(self.colors[5])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(curve_points)
            self.polygon_curve_points_type.append(curve_points_type)

        # calculate fairway bunker ring -> where fairway bunkers will be placed
        fairway_bunker_ring_points = self.__calc_outline_curve_points(
            line=False,
            points=self.outline_points,
            points_scale=self.outline_points_scale,
            width=self.outline_offset - 17
        )
        fairway_bunker_ring = self.__calc_polygon_outline(
            None,
            fairway_bunker_ring_points,
            [False for _ in fairway_bunker_ring_points]
        )

        if par > 3:
            fairway_bunker_curve_points = []
            for i in range(fairway_bunker_count):
                # set parameters
                y_pos = self.outline_points[0][1] - random.randint(150, distance - 50)
                offset = [random.randint(-5, 5), random.randint(-5, 5)]  
                # worm bunker
                if random.randint(0, 3) <= 2:
                    # set parameters
                    angle = radians(random.randint(-90, 90))  
                    offset_angle = radians(random.randint(110, 170))  
                    length = random.randint(8, 12)  
                    radius = random.randint(3, 6)  

                    # y_pos minus move direction
                    y_negation = False
                    x_negation = None
                    while True:
                        # calculate x_pos
                        np_fairway_bunker_ring = np.array(fairway_bunker_ring)
                        x_pos = fairway_bunker_ring[np.abs(np_fairway_bunker_ring[:, 1] - y_pos).argmin()][0]

                        start_point = [
                            x_pos + cos(angle) * (length / 2) + offset[0],
                            y_pos + sin(angle) * (length / 2) + offset[1]
                        ]
                        center_point = [x_pos + offset[0], y_pos + offset[1]]
                        end_point = [
                            x_pos + cos(offset_angle + angle) * (length / 2) + offset[0],
                            y_pos + sin(offset_angle + angle) * (length / 2) + offset[1]
                        ]

                        # calculate curve points
                        curve_points = self.generate_bunker_outline(
                            line_points=[start_point, center_point, end_point],
                            radius=radius
                        )
                        # 5m curve points outline
                        curve_5_points = self.generate_bunker_outline(
                            line_points=[start_point, center_point, end_point],
                            radius=radius + 5
                        )
                        # 12m curve points outline
                        curve_12_points = self.generate_bunker_outline(
                            line_points=[start_point, center_point, end_point],
                            radius=radius + 10
                        )

                        # check for intersections
                        for bunker_poly in fairway_bunker_curve_points + self.water_12_curve_points:
                            if Polygon(curve_5_points).intersects(Polygon(bunker_poly)):
                                # turn move direction down
                                if y_pos + 5 > distance - 50:
                                    y_negation = True
                                # move up or down
                                if y_negation:
                                    y_pos -= 5
                                else:
                                    y_pos += 5
                                break
                        else:
                            # check for intersection with other polygons
                            for path_curve_points in self.path_curve_points:
                                if len(path_curve_points) > 0 and Polygon(curve_5_points).intersects(
                                        Polygon(path_curve_points)):
                                    # move left right
                                    if x_negation is None and center_point[0] > 0:
                                        x_negation = True
                                    if x_negation:
                                        offset[0] -= 5
                                    else:
                                        offset[0] += 5
                                    break
                            else:
                                fairway_bunker_curve_points.append(curve_points)
                                self.bunker_5_curve_points.append(curve_5_points)
                                curve_points_type = [False for _ in curve_points]

                                # polygon outline
                                self.polygon_curve_12_points.append(curve_12_points)

                                # create new polygon
                                self.polygon_z_pos.append(1)
                                self.polygon_colors.append(self.colors[5])
                                self.polygon_curve.append([])
                                self.polygon_curve_points.append(curve_points)
                                self.polygon_curve_points_type.append(curve_points_type)
                                break

                # round bunker
                else:
                    # set parameters
                    radius = random.randint(4, 6)  

                    # y_pos minus move direction
                    y_negation = False
                    while True:
                        # calculate x_pos
                        np_fairway_bunker_ring = np.array(fairway_bunker_ring)
                        x_pos = fairway_bunker_ring[np.abs(np_fairway_bunker_ring[:, 1] - y_pos).argmin()][0]

                        # calculate curve points
                        curve_points, curve_points_type = self.__generate_circular_curve_points(
                            center=[x_pos + offset[0], y_pos + offset[1]],
                            radius=radius,
                            resolution=10
                        )
                        # calculate 5m curve outline points
                        curve_5_points, _ = self.__generate_circular_curve_points(
                            center=[x_pos + offset[0], y_pos + offset[1]],
                            radius=radius + 5,
                            resolution=10
                        )
                        # calculate 12m curve outline points
                        curve_12_points, _ = self.__generate_circular_curve_points(
                            center=[x_pos + offset[0], y_pos + offset[1]],
                            radius=radius + 10,
                            resolution=10
                        )

                        # check for intersections
                        for bunker_poly in fairway_bunker_curve_points + self.water_12_curve_points:
                            if Polygon(curve_5_points).intersects(Polygon(bunker_poly)):
                                # turn move direction down
                                if y_pos + 5 > distance - 50:
                                    y_negation = True
                                # move up or down
                                if y_negation:
                                    y_pos -= 5
                                else:
                                    y_pos += 5
                                break
                        else:
                            # check for intersection with other polygons
                            for path_curve_points in self.path_curve_points:
                                if len(path_curve_points) > 0 and Polygon(curve_5_points).intersects(
                                        Polygon(path_curve_points)):
                                    # move left right
                                    if x_pos + offset[0] > 0:
                                        offset[0] -= 5
                                    else:
                                        offset[0] += 5
                                    break
                            else:
                                fairway_bunker_curve_points.append(curve_points)
                                self.bunker_5_curve_points.append(curve_5_points)

                                # polygon outline
                                self.polygon_curve_12_points.append(curve_12_points)

                                # create new polygon
                                self.polygon_z_pos.append(1)
                                self.polygon_colors.append(self.colors[5])
                                self.polygon_curve.append([])
                                self.polygon_curve_points.append(curve_points)
                                self.polygon_curve_points_type.append(curve_points_type)
                                break

    # list num [integer/meter], index [integer/index]
    def __get_green_outline_curve_point(self, list_num: int, index: int):
        outline_list = getattr(self, f"green_{list_num}_curve_points")

        return outline_list[index if len(outline_list) - 1 > index else index - (len(outline_list) - 1)]

    # y [y coordinate]
    def __calc_center_for_y(self, y: float):
        # y is bigger than the biggest point
        if y > self.outline_points[0][1]:
            dx = self.outline_points[0][0] - self.outline_points[1][0]
            dy = self.outline_points[0][1] - self.outline_points[1][1]
            return dx / dy * (y - self.outline_points[1][1]) + self.outline_points[1][0]
        # y is smaller than the smallest point
        elif y < self.outline_points[-1][1]:
            dx = self.outline_points[-1][0] - self.outline_points[-2][0]
            dy = self.outline_points[-1][1] - self.outline_points[-2][1]
            return dx / dy * (y - self.outline_points[-2][1]) + self.outline_points[-2][0]
        # y is in range of points
        else:
            for i, p in enumerate(self.outline_points):
                if p[1] > y > self.outline_points[i + 1][1]:
                    dx = self.outline_points[i][0] - self.outline_points[i + 1][0]
                    dy = self.outline_points[i][1] - self.outline_points[i + 1][1]
                    return dx / dy * (y - self.outline_points[i + 1][1]) + self.outline_points[i + 1][0]

    # count [integer/count], distance [meter]
    def __generate_rough(self, count: int, distance: int):
        for i in range(count):
            # calculate rough ring -> where rough will be placed
            rough_ring = self.__re_mesh_polygon(
                curve_points=self.outline_curve_points,
                curve_points_type=[False for _ in self.outline_curve_points],
                accuracy="auto"
            )

            # select side
            side = "left" if random.randint(0, 1) == 0 else "right"
            if side == "left":
                rough_ring = [p for p in rough_ring if p[0] > self.__calc_center_for_y(p[1])]
            else:
                rough_ring = [p for p in rough_ring if p[0] < self.__calc_center_for_y(p[1])]

            # set parameters
            height = random.randint(50, distance // 2)  
            y_pos = self.outline_points[0][1] - random.randint(0, distance - height)  
            width = random.randint(12, 15)  

            # calculate x, y positions
            x_start = rough_ring[np.abs(np.array(rough_ring)[:, 1] - y_pos).argmin()][0]
            x_center = rough_ring[np.abs(np.array(rough_ring)[:, 1] - (y_pos - height / 2)).argmin()][0]
            x_end = rough_ring[np.abs(np.array(rough_ring)[:, 1] - (y_pos - height)).argmin()][0]

            points_scale = [1, random.randint(10, 15) / 10, 1]  
            # calculate outline curve
            curve_points = self.__calc_outline_curve_points(
                line=False,
                points=[[x_start, y_pos], [x_center, y_pos - height / 2], [x_end, y_pos - height]],
                points_scale=points_scale,
                width=width
            )
            # calculate curve 12 points -> 12m offset
            curve_12_points = self.__calc_outline_curve_points(
                line=False,
                points=[[x_start, y_pos], [x_center, y_pos - height / 2], [x_end, y_pos - height]],
                points_scale=points_scale,
                width=width + 10
            )

            for cut_poly in self.bunker_5_curve_points + [self.green_14_curve_points] + [self.tee_outline_curve_points]:
                # calculate intersection points
                cut_poly = self.__re_mesh_polygon(
                    curve_points=cut_poly,
                    curve_points_type=[False for _ in cut_poly],
                    accuracy=5
                )
                if Polygon(cut_poly).is_simple:
                    curve_points = self.__cut_polygon_from_polygon(curve_points, cut_poly)[0]

            # curve outline
            self.polygon_curve_12_points.append(curve_12_points)

            # calculate curve points type
            curve_points_type = [False for _ in curve_points]

            # create new polygon
            self.polygon_z_pos.insert(0, 1)
            self.polygon_colors.insert(0, self.colors[4])
            self.polygon_curve.insert(0, [])
            self.polygon_curve_points.insert(0, curve_points)
            self.polygon_curve_points_type.insert(0, curve_points_type)

    # count [integer/count]
    def __generate_out(self, count: int):
        for i in range(count):
            # calculate rough ring -> where rough will be placed
            rough_ring = self.__re_mesh_polygon(
                curve_points=self.outline_curve_points,
                curve_points_type=[False for _ in self.outline_curve_points],
                accuracy="auto"
            )

            # set parameters
            start = random.randint(0, len(rough_ring))  
            length = random.randint(10, len(rough_ring) // 2)  
            width = random.randint(5, 6)  

            if start + length < len(rough_ring):
                points = [p for p in rough_ring[start:start + length]]
            else:
                points = [p for p in rough_ring[start:] + rough_ring[:length - (len(rough_ring) - start)]]

            points_scale = [random.randint(10, 15) / 10 for _ in points]  
            # calculate outline curve
            curve_points = self.__calc_outline_curve_points(
                line=False,
                points=points,
                points_scale=points_scale,
                width=width
            )

            # calculate curve 12 points -> 12m offset
            curve_12_points = self.__calc_outline_curve_points(
                line=False,
                points=points,
                points_scale=points_scale,
                width=width + 10
            )

            for cut_poly in [self.tee_outline_curve_points] + [self.green_14_curve_points]:
                # calculate intersection points
                curve_points = self.__cut_polygon_from_polygon(curve_points, cut_poly)[0]

            self.polygon_curve_12_points.append(curve_12_points)
            # calculate curve points type
            curve_points_type = [False for _ in curve_points]

            # create new polygon
            self.polygon_z_pos.append(0)
            self.polygon_colors.append(self.colors[9])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(curve_points)
            self.polygon_curve_points_type.append(curve_points_type)

    def __generate_fairway(self, par: int):
        # fairway start
        if par > 3:
            fairway_start = random.randint(100, 130)

            # calculate fairway points
            fairway_points = copy.deepcopy(self.outline_points)
            dx = fairway_points[1][0] - fairway_points[0][0]
            dy = fairway_points[1][1] - fairway_points[0][1]
            hyp = sqrt(dx ** 2 + dy ** 2)
            # change starting point
            fairway_points[0] = [
                fairway_points[0][0] + dx / hyp * fairway_start,
                fairway_points[0][1] + dy / hyp * fairway_start
            ]

            # generate fairway outline
            curve_points = [self.__calc_outline_curve_points(
                line=False,
                points=fairway_points,
                points_scale=self.outline_points_scale,
                width=self.outline_offset - random.randint(17, 20)
            )]

            # cut out polygons
            for cut_poly in self.polygon_curve_12_points:
                for poly_i, poly in enumerate(curve_points):
                    # try to solve self-intersecting polygons
                    if not Polygon(cut_poly).is_simple:
                        cut_poly = Polygon(cut_poly).buffer(0)
                        cut_poly = cut_poly.exterior.coords[:-1]
                    if not Polygon(poly).is_simple:
                        poly = Polygon(poly).buffer(0)
                        poly = poly.exterior.coords[:-1]

                    # cut out polygon
                    new_polygon = self.__cut_polygon_from_polygon(poly, cut_poly)
                    curve_points[poly_i] = new_polygon[0]

                    if len(new_polygon) > 1:
                        for i, new_poly in enumerate(new_polygon[1:]):
                            curve_points.append(new_poly)

            # re mesh polygons
            for i, poly in enumerate(curve_points):
                if len(poly) > 2:
                    curve_points[i] = self.__re_mesh_polygon(poly, [False for _ in poly], 10)

            # fairway near green
            to_green_dis = random.randint(40, 50)  
            entrance_width = random.randint(10, 15)  
            rotation = atan2(
                self.outline_points[-2][0] - self.outline_points[-1][0],
                self.outline_points[-2][1] - self.outline_points[-1][1]
            )

            cut_poly = self.__calc_rectangle_cords(self.outline_points[-1], 100, to_green_dis * 2, rotation)

            # cut out green section
            poly_index = None
            for i, curve in enumerate(curve_points):
                if Polygon(curve).intersects(Polygon(cut_poly)):
                    if not Polygon(curve).is_simple:
                        curve = Polygon(curve).buffer(0)[0]
                        curve = curve.exterior.coords[:-1]

                    curve_points[i] = self.__cut_polygon_from_polygon(curve, cut_poly)[0]
                    if len(curve_points[i]) > 2:
                        poly_index = i
                        break

            if poly_index is not None:
                curve = Polygon(curve_points[poly_index]).buffer(0)
                curve_points[poly_index] = curve.exterior.coords[:-1]

                # get line to cut fairway
                dx = self.outline_points[-2][0] - self.outline_points[-1][0]
                dy = self.outline_points[-2][1] - self.outline_points[-1][1]
                hyp = sqrt(dx ** 2 + dy ** 2)
                new_x = self.outline_points[-1][0] + dx / hyp * to_green_dis
                new_y = self.outline_points[-1][1] + dy / hyp * to_green_dis

                angle = atan2(dx, dy)
                line = [
                    [new_x + cos(-angle) * 50, new_y + sin(-angle) * 50],
                    [new_x - cos(-angle) * 50, new_y - sin(-angle) * 50],
                ]

                distances = [self.__distance_point_to_line(p, line) for p in curve_points[poly_index]]
                smallest_index = min(distances.index(sorted(distances)[0]), distances.index(sorted(distances)[1]))
                fairway_center_point = [
                    (curve_points[poly_index][smallest_index][0] + curve_points[poly_index][smallest_index + 1][0]) / 2,
                    (curve_points[poly_index][smallest_index][1] + curve_points[poly_index][smallest_index + 1][1]) / 2
                ]

                rotation = atan2(
                    fairway_center_point[0] - self.outline_points[-1][0],
                    fairway_center_point[1] - self.outline_points[-1][1]
                )

            # green outline
            center = [
                self.outline_points[-1][0] + sin(rotation) * to_green_dis / 2,
                self.outline_points[-1][1] + cos(rotation) * to_green_dis / 2
            ]
            cut_poly = self.__calc_rectangle_cords(center, 100, to_green_dis, rotation)
            cut_polygon = Polygon(cut_poly)

            # remove points at green entrance
            pop_list = []
            for i, p in enumerate(self.green_2_curve_points):
                if cut_polygon.contains(Point(p)):
                    distance = self.__distance_point_to_line(p, [self.outline_points[-1], self.outline_points[-2]])
                    if distance < entrance_width / 2:
                        pop_list.append(i)

            for i in reversed(pop_list):
                self.green_2_curve_points.pop(i)

            # find curve index
            center = [
                self.outline_points[-1][0] - sin(rotation) * (to_green_dis / 2 - 2),
                self.outline_points[-1][1] - cos(rotation) * (to_green_dis / 2 - 2)
            ]
            left_center = [
                self.outline_points[-1][0] - cos(- rotation) * 25,
                self.outline_points[-1][1] - sin(- rotation) * 25
            ]
            right_center = [
                self.outline_points[-1][0] + cos(- rotation) * 25,
                self.outline_points[-1][1] + sin(- rotation) * 25
            ]
            cut_poly = Polygon(self.__calc_rectangle_cords(center, 100, to_green_dis, rotation))
            left_poly = self.__calc_rectangle_cords(left_center, 50, to_green_dis, rotation)
            right_poly = self.__calc_rectangle_cords(right_center, 50, to_green_dis, rotation)

            # cut back of green
            points = [p for p in self.green_2_curve_points if not cut_poly.contains(Point(p))]
            # transform to left and right points
            left_polygon, right_polygon = Polygon(left_poly), Polygon(right_poly)
            left_points = [p for p in points if left_polygon.contains(Point(p))]
            right_points = [p for p in points if right_polygon.contains(Point(p))]

            # calculate distances
            line = [self.outline_points[-1], self.outline_points[-2]]

            # calculate green entrance points
            right_point = [
                self.outline_points[-1][0] + sin(rotation) * (to_green_dis / 2) + cos(- rotation) * entrance_width / 2,
                self.outline_points[-1][1] + cos(rotation) * (to_green_dis / 2) + sin(- rotation) * entrance_width / 2
            ]
            left_point = [
                self.outline_points[-1][0] + sin(rotation) * (to_green_dis / 2) - cos(- rotation) * entrance_width / 2,
                self.outline_points[-1][1] + cos(rotation) * (to_green_dis / 2) - sin(- rotation) * entrance_width / 2
            ]

            # left
            left_index = self.green_2_curve_points.index(left_points[-1])
            right_index = self.green_2_curve_points.index(right_points[0])

            if right_index < left_index:
                self.green_2_curve_points.insert(min(right_index, left_index), right_point)
                self.green_2_curve_points.insert(min(right_index, left_index), left_point)
            else:
                self.green_2_curve_points.insert(min(right_index, left_index), left_point)
                self.green_2_curve_points.insert(min(right_index, left_index), right_point)
            # reshape green list
            green_points = self.green_2_curve_points[min(right_index, left_index) + 1:] + \
                           self.green_2_curve_points[:min(right_index, left_index) + 1]

            # find fairway section end points
            if poly_index is None or len(curve_points[poly_index]) < 3:
                green_points.append([
                    self.outline_points[-1][0] + sin(rotation) * (to_green_dis / 2 + 5),
                    self.outline_points[-1][1] + cos(rotation) * (to_green_dis / 2 + 5)
                ])

                curve_points.append(green_points)
            else:
                first_dis = sqrt((curve_points[poly_index][smallest_index + 1][0] - green_points[0][0]) ** 2 +
                                 (curve_points[poly_index][smallest_index + 1][1] - green_points[0][1]) ** 2)
                last_dis = sqrt((curve_points[poly_index][smallest_index + 1][0] - green_points[-1][0]) ** 2 +
                                (curve_points[poly_index][smallest_index + 1][1] - green_points[-1][1]) ** 2)

                if last_dis < first_dis:
                    for p in reversed(green_points):
                        curve_points[poly_index].insert(smallest_index + 1, p)
                else:
                    for p in green_points:
                        curve_points[poly_index].insert(smallest_index + 1, p)

            curve_points_type = [[False for _ in curve] for curve in curve_points]

            # create new polygon
            for curve, curve_type in zip(curve_points, curve_points_type):
                if len(curve) > 2:
                    self.polygon_z_pos.insert(0, 1)
                    self.polygon_colors.insert(0, self.colors[2])
                    self.polygon_curve.insert(0, [])
                    self.polygon_curve_points.insert(0, curve)
                    self.polygon_curve_points_type.insert(0, curve_type)
        # for par 3
        else:
            # fairway near green
            to_green_dis = random.randint(40, 50)  
            entrance_width = random.randint(10, 15)  
            rotation = atan2(
                self.outline_points[-2][0] - self.outline_points[-1][0],
                self.outline_points[-2][1] - self.outline_points[-1][1]
            )

            # green outline
            center = [
                self.outline_points[-1][0] + sin(rotation) * to_green_dis / 2,
                self.outline_points[-1][1] + cos(rotation) * to_green_dis / 2
            ]
            cut_poly = self.__calc_rectangle_cords(center, 100, to_green_dis, rotation)
            cut_polygon = Polygon(cut_poly)

            # remove points at green entrance
            pop_list = []
            for i, p in enumerate(self.green_2_curve_points):
                if cut_polygon.contains(Point(p)):
                    distance = self.__distance_point_to_line(p, [self.outline_points[-1], self.outline_points[-2]])
                    if distance < entrance_width / 2:
                        pop_list.append(i)

            for i in reversed(pop_list):
                self.green_2_curve_points.pop(i)

            # find curve index
            center = [
                self.outline_points[-1][0] - sin(rotation) * (to_green_dis / 2 - 2),
                self.outline_points[-1][1] - cos(rotation) * (to_green_dis / 2 - 2)
            ]
            left_center = [
                self.outline_points[-1][0] - cos(- rotation) * 25,
                self.outline_points[-1][1] - sin(- rotation) * 25
            ]
            right_center = [
                self.outline_points[-1][0] + cos(- rotation) * 25,
                self.outline_points[-1][1] + sin(- rotation) * 25
            ]
            cut_poly = Polygon(self.__calc_rectangle_cords(center, 100, to_green_dis, rotation))
            left_poly = self.__calc_rectangle_cords(left_center, 50, to_green_dis, rotation)
            right_poly = self.__calc_rectangle_cords(right_center, 50, to_green_dis, rotation)

            # cut back of green
            points = [p for p in self.green_2_curve_points if not cut_poly.contains(Point(p))]
            # transform to left and right points
            left_polygon, right_polygon = Polygon(left_poly), Polygon(right_poly)
            left_points = [p for p in points if left_polygon.contains(Point(p))]
            right_points = [p for p in points if right_polygon.contains(Point(p))]

            # calculate distances
            line = [self.outline_points[-1], self.outline_points[-2]]

            # calculate green entrance points
            right_point = [
                self.outline_points[-1][0] + sin(rotation) * (to_green_dis / 2) + cos(- rotation) * entrance_width / 2,
                self.outline_points[-1][1] + cos(rotation) * (to_green_dis / 2) + sin(- rotation) * entrance_width / 2
            ]
            left_point = [
                self.outline_points[-1][0] + sin(rotation) * (to_green_dis / 2) - cos(- rotation) * entrance_width / 2,
                self.outline_points[-1][1] + cos(rotation) * (to_green_dis / 2) - sin(- rotation) * entrance_width / 2
            ]

            # left
            if self.__distance_point_to_line(left_points[0], line) > self.__distance_point_to_line(left_points[-1], line):
                left_index = self.green_2_curve_points.index(left_points[-1])
            else:
                left_index = self.green_2_curve_points.index(left_points[0])

            # right
            if self.__distance_point_to_line(right_points[0], line) > self.__distance_point_to_line(right_points[-1], line):
                right_index = self.green_2_curve_points.index(right_points[-1])
            else:
                right_index = self.green_2_curve_points.index(right_points[0])

            if right_index < left_index:
                self.green_2_curve_points.insert(min(right_index, left_index), right_point)
                self.green_2_curve_points.insert(min(right_index, left_index), left_point)
            else:
                self.green_2_curve_points.insert(min(right_index, left_index), left_point)
                self.green_2_curve_points.insert(min(right_index, left_index), right_point)
            # reshape green list
            green_points = self.green_2_curve_points[min(right_index, left_index) + 1:] + \
                           self.green_2_curve_points[:min(right_index, left_index) + 1]

            green_points.append([
                self.outline_points[-1][0] + sin(rotation) * (to_green_dis / 2 + 5),
                self.outline_points[-1][1] + cos(rotation) * (to_green_dis / 2 + 5)
            ])

            # create new polygon
            self.polygon_z_pos.insert(0, 1)
            self.polygon_colors.insert(0, self.colors[2])
            self.polygon_curve.insert(0, [])
            self.polygon_curve_points.insert(0, green_points)
            self.polygon_curve_points_type.insert(0, [False for _ in green_points])

    # tree_count [integer/count]
    def __generate_trees(self, tree_count: int):
        # create possible tree position map
        tree_map = np.zeros(self.SIZE)

        # create occupancy map
        for i, poly in enumerate(self.polygon_curve_points):
            for color in [self.colors[2], self.colors[5], self.colors[8], self.colors[10], self.colors[11]]:
                if np.array_equal(color, self.polygon_colors[i]):
                    # calc polygon points
                    outline_arr = np.array(poly, dtype=np.int32)
                    outline_arr[:, 0] += self.center[0]
                    outline_arr[:, 1] += self.center[1]
                    outline_arr = outline_arr.reshape((1, -1, 2))

                    # draw points on to the screen
                    cv2.fillPoly(tree_map, [outline_arr], 1)
                    cv2.polylines(tree_map, [outline_arr], isClosed=True, color=1, thickness=3)

                    break

        # Tee
        outline_arr = np.array(self.tee_outline_curve_points, dtype=np.int32)
        outline_arr[:, 0] += self.center[0]
        outline_arr[:, 1] += self.center[1]
        outline_arr = outline_arr.reshape((1, -1, 2))

        # draw points on to the screen
        cv2.fillPoly(tree_map, [outline_arr], 1)
        cv2.polylines(tree_map, [outline_arr], isClosed=True, color=1, thickness=3)

        # center poly
        center_curve_points = self.__calc_outline_curve_points(
            line=False,
            points=self.outline_points,
            points_scale=self.outline_points_scale,
            width=15
        )
        outline_arr = np.array(center_curve_points, dtype=np.int32)
        outline_arr[:, 0] += self.center[0]
        outline_arr[:, 1] += self.center[1]
        outline_arr = outline_arr.reshape((1, -1, 2))

        # draw points on to the screen
        cv2.fillPoly(tree_map, [outline_arr], 1)
        cv2.polylines(tree_map, [outline_arr], isClosed=True, color=1, thickness=3)

        # Hole Outline
        outline_arr = np.array(self.outline_curve_points, dtype=np.int32)
        outline_arr[:, 0] += self.center[0]
        outline_arr[:, 1] += self.center[1]
        outline_arr = outline_arr.reshape((1, -1, 2))

        # draw points on to the screen
        hole_outline_mask = np.zeros_like(tree_map)
        cv2.fillPoly(hole_outline_mask, [outline_arr], 1)
        cv2.polylines(hole_outline_mask, [outline_arr], isClosed=True, color=1, thickness=3)

        tree_map = np.where(hole_outline_mask == 0, 1, tree_map)

        possible_tree_cords = np.transpose(np.where(tree_map == 0)).tolist()

        for i in range(tree_count):
            tree_pos = possible_tree_cords[random.randint(0, len(possible_tree_cords))]  
            tree_radius = random.randint(6, 10)  

            curve_points = []
            # create curve points
            for i in range(tree_radius):
                # calculate circle position
                x_pos = sin(radians(360 / tree_radius * i)) * tree_radius + tree_pos[1] - self.center[0]
                y_pos = cos(radians(360 / tree_radius * i)) * tree_radius + tree_pos[0] - self.center[1]

                curve_points.append([x_pos, y_pos])

            # add polygon
            self.polygon_z_pos.append(-1)
            self.polygon_colors.append(self.colors[7])
            self.polygon_curve.append([])
            self.polygon_curve_points.append(curve_points)
            self.polygon_curve_points_type.append([False for _ in curve_points])

    def __generate_semi_rough(self):
        curve_points = self.__calc_outline_curve_points(
            line=False,
            points=self.outline_points,
            points_scale=self.outline_points_scale,
            width=self.outline_offset + 5
        )
        curve_points_type = [False for _ in curve_points]

        self.polygon_z_pos.insert(0, 1)
        self.polygon_colors.insert(0, self.colors[3])
        self.polygon_curve.insert(0, [])
        self.polygon_curve_points.insert(0, curve_points)
        self.polygon_curve_points_type.insert(0, curve_points_type)

    # point [x, y point], line list[two x, y points]
    @staticmethod
    def __distance_point_to_line(point: [float, float], line: [[float, float], [float, float]]):
        # set parameters
        point = np.array(point)
        line_point1 = np.array(line[0])
        line_point2 = np.array(line[1])

        # Calculate distance
        line_vector = line_point2 - line_point1
        point_vector = point - line_point1
        projection = np.dot(point_vector, line_vector) / np.dot(line_vector, line_vector)
        closest_point = line_point1 + projection * line_vector

        return np.linalg.norm(point - closest_point)

    # poly_1 list[x, y points], poly_2 list[x, y points]
    @staticmethod
    def __cut_polygon_from_polygon(poly: list[[float, float]], cut_poly: list[[float, float]]):
        poly1 = Polygon(poly)
        poly2 = Polygon(cut_poly)
        result = poly1.difference(poly2)

        if type(result) == MultiPolygon:
            return [list(p.exterior.coords) for p in result.geoms]
        else:
            return [list(result.exterior.coords)]

    # center [x, y point], width [meter], height [meter], rotation [radians]
    @staticmethod
    def __calc_rectangle_cords(center: [int, int], width: int, height: int, rotation: float):
        # Calculate the coordinates of the four corners
        return [
            [center[0] - (width / 2) * cos(rotation) - (height / 2) * sin(rotation),
             center[1] + (width / 2) * sin(rotation) - (height / 2) * cos(rotation)],
            [center[0] + (width / 2) * cos(rotation) - (height / 2) * sin(rotation),
             center[1] - (width / 2) * sin(rotation) - (height / 2) * cos(rotation)],
            [center[0] + (width / 2) * cos(rotation) + (height / 2) * sin(rotation),
             center[1] - (width / 2) * sin(rotation) + (height / 2) * cos(rotation)],
            [center[0] - (width / 2) * cos(rotation) + (height / 2) * sin(rotation),
             center[1] + (width / 2) * sin(rotation) + (height / 2) * cos(rotation)]
        ]

    # visualise outline
    def __visualise_polygons(self):
        # calc indices
        z_values = np.sort(np.unique(self.polygon_z_pos))[::-1]
        indices = []
        for val in z_values:
            indices.append(list(np.where(np.array(self.polygon_z_pos) == val)[0]))

        self.polygon_widgets = [Advanced_Polygon(self.canvas, [], (0, 0, 0)) for _ in self.polygon_z_pos]

        for z_val in indices:
            for i in z_val:

                # calculate polygon outline
                self.polygon_curve[i] = self.__calc_polygon_outline(i)

                # calculate offsets
                points = copy.deepcopy(self.polygon_curve[i])
                for p in points:
                    p[0] += self.center[0]
                    p[1] += self.center[1]

                # visualise
                self.polygon_widgets[i].set_color(self.polygon_colors[i])
                self.polygon_widgets[i].set_pos(points)
                self.polygon_widgets[i].draw()

    # calculate polygon outline; poly_index [integer/index], curve_points list[x, y points], curve_points_type list[bool]
    def __calc_polygon_outline(self, poly_index: int = None, curve_points: list[list[int, int]] = None,
                               curve_points_type: list[bool] = None):
        # get curve points from polygon list
        if poly_index is not None:
            curve_points = self.polygon_curve_points[poly_index]
            curve_points_type = self.polygon_curve_points_type[poly_index]

        # initialise points & outline
        points = [curve_points[-1]] + curve_points + curve_points[0:3]
        outline = []

        # calculate curve
        for i in range(len(points) - 4):
            # first point
            vector_points = [points[i + 1]]
            if not curve_points_type[i]:
                vector_points.append(self.__get_vector_points(points[i], points[i + 1], points[i + 2])[1])
            # second point
            index = i + 1 if len(curve_points_type) > i + 1 else 0
            if not curve_points_type[index]:
                vector_points.append(self.__get_vector_points(points[i + 1], points[i + 2], points[i + 3])[0])
            vector_points.append(points[i + 2])

            # add curve points to outline
            for pos in self.__calc_bezier(vector_points):
                outline.append(pos)

        return outline

    # expand a point; points [list[x, y points]], next_point [x, y point], expand_dis [meter]
    @staticmethod
    def __expand_point(points: list[int, int], next_point: list[int, int], expand_dis: int = 10):
        delta_x, delta_y = points[0] - next_point[0], points[1] - next_point[1]
        hyp = sqrt(delta_x ** 2 + delta_y ** 2)

        new_x = delta_x / hyp * (hyp + expand_dis) + next_point[0]
        new_y = delta_y / hyp * (hyp + expand_dis) + next_point[1]

        return [new_x, new_y]

    # curve_points list[x, y points], curve_points_type [bool], resolution [int/auto]
    def __re_mesh_polygon(self, curve_points: list[list[int, int]], curve_points_type: list[bool], accuracy = "auto"):
        curve = self.__calc_polygon_outline(curve_points=curve_points, curve_points_type=curve_points_type)
        length = Polygon(curve).length
        curve += curve[:10]

        # calculate resolution
        resolution = floor(length / 20) if accuracy == "auto" else floor(length / accuracy)

        new_curve = []
        index = 0
        index_dis = 0
        for i in range(resolution):
            step_length = length / resolution
            while True:
                dx = (curve[index + 1][0] - curve[index][0])
                dy = (curve[index + 1][1] - curve[index][1])
                element_dis = sqrt(dx ** 2 + dy ** 2)
                # step length is bigger than element length
                if element_dis - index_dis < step_length:
                    step_length -= (element_dis - index_dis)
                    index += 1
                    index_dis = 0
                # step length shorter than element length
                else:
                    index_dis += step_length
                    new_curve.append(
                        [curve[index][0] + dx / element_dis * index_dis,
                         curve[index][1] + dy / element_dis * index_dis]
                    )

                    break

        return new_curve

    # line_points list[x, y points], radius [meter]
    @staticmethod
    def generate_bunker_outline(line_points: list[list[float, float]], radius: int):
        return LineString(line_points).buffer(radius, join_style=0, resolution=2).exterior.coords[:-1]

    # generate noise; size [meter], length [integer/count], substeps [integer]
    @staticmethod
    def __generate_noise(size, length, substeps: int = 2):
        # calculate noise points
        noise_points = [random.randint(0, 10) / 10 for _ in range(substeps + 2)]  
        noise_points[-1] = noise_points[0]

        noise = []
        # convert to smooth noise
        for i, p in enumerate(noise_points[1:]):
            start, delta = noise_points[i], p - noise_points[i]
            # calculate sin curve
            for index in range(floor(length / (len(noise_points) - 1))):
                noise.append(cos((index / floor(
                    length / (len(noise_points) - 1))) * pi - pi) * delta / 2 + start + delta / 2)

        # add to match length
        for i in range(length - len(noise)):
            noise.append(noise[0])

        # set ending to start point
        noise[-1] = noise[0]

        return [i * size - (size / 2) for i in noise]

    # get bezier vector points; p1 [x, y point], p2 [x, y point], p3 [x, y point], p4 [x, y point]
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
            return (p2[0] - p13_dis / dx * (p12_dis / 3), p2[1] - p13_dis / dx * (p12_dis / 3) * (dy / dx)), (
                p2[0] + p13_dis / dx * (p23_dis / 3), p2[1] + p13_dis / dx * (p23_dis / 3) * (dy / dx))
        else:
            return (p2[0] - p13_dis / dy * (p12_dis / 3) * (dx / dy), p2[1] - p13_dis / dy * (p12_dis / 3)), (
                p2[0] + p13_dis / dy * (p23_dis / 3) * (dx / dy), p2[1] + p13_dis / dy * (p23_dis / 3))

    # calculate bezier curve; points list[x, y points]
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
            curve_points.append(list(point))
        return curve_points
