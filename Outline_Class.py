from Map import Map
from math import *
import copy


class Outline_Generator(object):
    def __init__(self, map: Map):
        self.map = map
        self.edit_mode = True

        # offsets
        self.offset = 25
        self.fade_offset = 10
        self.ratio = None

        # point list
        self.points = []
        self.points_scale = []
        self.curve_points = []
        self.fade_curve_points = []

        # outline points list
        self.outline_points = []
        self.fade_outline_points = []

        # selected point
        self.selected = None
        self.scale_dis = None
        self.start_scale = None

    # generate outline
    def generate_outline(self, par, start_pos: (float, float), end_pos: (float, float), ratio: float):
        self.ratio = ratio
        self.edit_mode = True

        # starting point
        self.points.append(list(start_pos))
        self.points_scale.append(1)
        # intermediate points
        for i in range(par - 3):
            i += 1
            # calculate delta
            delta_x = end_pos[0] - start_pos[0]
            delta_y = end_pos[1] - start_pos[1]
            # add point
            self.points.append([start_pos[0] + delta_x / (par - 2) * i, start_pos[1] + delta_y / (par - 2) * i])
            self.points_scale.append(1.4)
        # ending point
        self.points.append(list(end_pos))
        self.points_scale.append(1)

        # calculate curve points
        self.calc_curve_points()

        # draw points
        self.draw_points()

    # calculate curve points
    def calc_curve_points(self):
        # fill curve pints
        self.curve_points = [[0, 0]] + [[0, 0] for _ in range(len(self.points) * 2)] + [[0, 0]]
        self.fade_curve_points = [[0, 0]] + [[0, 0] for _ in range(len(self.points) * 2)] + [[0, 0]]

        for i, p in enumerate(self.points):
            # first points
            if i == 0:
                delta_x, delta_y = self.points[i + 1][0] - p[0], self.points[i + 1][1] - p[1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * self.offset * self.points_scale[i] / self.ratio) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else self.offset * self.points_scale[i] / self.ratio
                self.curve_points[0] = [p[0] - dx, p[1] - dy]
                self.curve_points[2] = [p[0] + dx, p[1] + dy]

                # perpendicular fade offset
                dx = - (delta_y * (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio
                self.fade_curve_points[0] = [p[0] - dx, p[1] - dy]
                self.fade_curve_points[2] = [p[0] + dx, p[1] + dy]

                # parallel offset
                dx = - (delta_x * self.offset * self.points_scale[i] / self.ratio) / distance
                dy = - (delta_y * - dx) / delta_x if delta_x != 0 else self.offset * self.points_scale[i] / self.ratio
                self.curve_points[1] = [p[0] + dx, p[1] + dy]

                # parallel fade offset
                dx = - (delta_x * (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio) / distance
                dy = - (delta_y * - dx) / delta_x if delta_x != 0 else (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio
                self.fade_curve_points[1] = [p[0] + dx, p[1] + dy]

            # intermediate points
            elif i != len(self.points) - 1:
                delta_x, delta_y = self.points[i + 1][0] - self.points[i - 1][0], self.points[i + 1][1] - self.points[i - 1][1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * self.offset * self.points_scale[i] / self.ratio) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else self.offset * self.points_scale[i] / self.ratio
                self.curve_points[i + 2] = [p[0] + dx, p[1] + dy]
                self.curve_points[len(self.curve_points) - i] = [p[0] - dx, p[1] - dy]

                # perpendicular fade offset
                dx = - (delta_y * (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio
                self.fade_curve_points[i + 2] = [p[0] + dx, p[1] + dy]
                self.fade_curve_points[len(self.fade_curve_points) - i] = [p[0] - dx, p[1] - dy]

            # last points
            else:
                delta_x, delta_y = p[0] - self.points[i - 1][0], p[1] - self.points[i - 1][1]
                distance = sqrt(delta_x ** 2 + delta_y ** 2)

                # perpendicular offset
                dx = - (delta_y * self.offset * self.points_scale[i] / self.ratio) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else self.offset * self.points_scale[i] / self.ratio
                self.curve_points[len(self.points) + 1] = [p[0] + dx, p[1] + dy]
                self.curve_points[len(self.points) + 3] = [p[0] - dx, p[1] - dy]

                # perpendicular fade_offset
                dx = - (delta_y * (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio) / distance
                dy = (delta_x * - dx) / delta_y if delta_y != 0 else (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio
                self.fade_curve_points[len(self.points) + 1] = [p[0] + dx, p[1] + dy]
                self.fade_curve_points[len(self.points) + 3] = [p[0] - dx, p[1] - dy]

                # parallel offset
                dx = - (delta_x * self.offset * self.points_scale[i] / self.ratio) / distance
                dy = - (delta_y * - dx) / delta_x if delta_x != 0 else self.offset * self.points_scale[i] / self.ratio
                self.curve_points[len(self.points) + 2] = [p[0] - dx, p[1] - dy]

                # parallel offset
                dx = - (delta_x * (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio) / distance
                dy = - (delta_y * - dx) / delta_x if delta_x != 0 else (self.offset * self.points_scale[i] + self.fade_offset) / self.ratio
                self.fade_curve_points[len(self.points) + 2] = [p[0] - dx, p[1] - dy]

        if self.edit_mode:
            # draw curve points
            for i, p in enumerate(self.curve_points):
                if self.map.circle_exists(f"OCP{i}"):
                    self.map.set_circle_pos(f"OCP{i}", p[0], p[1])
                else:
                    self.map.add_circle(f"OCP{i}", p[0], p[1], 3, color=(0, 0, 0))

            # draw connection line
            for i, p in enumerate(self.points):
                if i > 0:
                    if self.map.line_exists(f"OCL{i}"):
                        self.map.set_line_pos(f"OCL{i}", self.points[i - 1][0], self.points[i - 1][1], p[0], p[1])
                    else:
                        self.map.add_line(f"OCL{i}", self.points[i - 1][0], self.points[i - 1][1], p[0], p[1], 1, color=(0, 0, 0))

            # draw points
            self.draw_points()

        # calculate outline
        self.__calc_outline("outline")
        if self.map.lines_exists("Hole_Outline"):
            self.map.set_lines_pos("Hole_Outline", copy.deepcopy(self.outline_points))
        else:
            self.map.add_lines("Hole_Outline", copy.deepcopy(self.outline_points), 3, (0, 0, 0), True)

        # calculate fade outline
        self.__calc_outline("fade_outline")
        if self.map.lines_exists("Hole_fade_Outline"):
            self.map.set_lines_pos("Hole_fade_Outline", copy.deepcopy(self.fade_outline_points))
        else:
            self.map.add_lines("Hole_fade_Outline", copy.deepcopy(self.fade_outline_points), 1, (0, 0, 0), True)

        self.map.draw()

    # draw main points
    def draw_points(self):
        for i, p in enumerate(self.points):
            # reposition point
            if self.map.circle_exists(f"OP{i}"):
                self.map.set_circle_pos(f"OP{i}", p[0], p[1])
            # create new point
            else:
                self.map.add_circle(f"OP{i}", p[0], p[1], 5, color=(0, 0, 0))

    # load from data
    def load_data(self, ratio: float, points: list[[float, float]], points_scale: list[float]):
        # assign data
        self.ratio = ratio
        self.points = points
        self.points_scale = points_scale

        # calculate curve points
        self.calc_curve_points()

    # get information
    def get_data(self) -> [list[[float, float]], list[float]]:
        return self.points, self.points_scale

    # clear
    def clear(self):
        # disable edit mode
        self.edit_mode = True
        self.disable_edit_mode()

        # clear the outlines
        if self.map.lines_exists("Hole_Outline"):
            self.map.clear_lines("Hole_Outline")
            self.map.clear_lines("Hole_fade_Outline")

        # clear lists
        self.points.clear()
        self.points_scale.clear()

    # enable edit mode
    def enable_edit_mode(self):
        # enable edit mode
        self.edit_mode = True

        # visualise
        self.draw_points()
        self.calc_curve_points()

    # disable edit mode
    def disable_edit_mode(self):
        if self.edit_mode:
            # clear visualisation
            for i in range(len(self.points)):
                # erase points
                if self.map.circle_exists(f"OP{i}"):
                    self.map.clear_circle(f"OP{i}")
                # erase connection line
                if i > 0 and self.map.line_exists(f"OCL{i}"):
                    self.map.clear_line(f"OCL{i}")
                # erase support points
                if i == 0 and self.map.circle_exists(f"OCP0"):
                    self.map.clear_circle(f"OCP0")
                if self.map.circle_exists(f"OCP{i * 2 + 1}"):
                    self.map.clear_circle(f"OCP{i * 2 + 1}")
                    self.map.clear_circle(f"OCP{i * 2 + 2}")
                if i == len(self.points) - 1 and self.map.circle_exists(f"OCP{i * 2 + 3}"):
                    self.map.clear_circle(f"OCP{i * 2 + 3}")

            # disable edit mode
            self.edit_mode = False

    # Mouse: left click
    def button_1(self, event):
        if self.edit_mode:
            # unselect selected point
            if self.selected is not None:
                self.map.circles[f"OP{self.selected}"].set_color(color=(0, 0, 0))

                self.selected = None

            # check if a point is clicked
            for i in range(len(self.points)):
                if self.map.circle_exists(f"OP{i}") and self.map.circles[f"OP{i}"].is_pressed(event):
                    self.selected = i

                    # change outline
                    self.map.circles[f"OP{i}"].set_color(color=(0, 0, 0), outline=(255, 255, 255))
                    break

            else:
                # check if a connection line has been clicked
                for i in range(len(self.points) - 1):
                    # define points
                    p1, p2 = self.points[i], self.points[i + 1]
                    x, y = self.map.get_click_pos(event)
                    # calculate distance to line
                    to_line_dis = self.distance_to_line_segment(x, y, p1[0], p1[1], p2[0], p2[1])

                    # check if lines has been clicked
                    if to_line_dis < 5:
                        # add point
                        self.points.insert(i + 1, list(self.map.get_click_pos(event)))
                        self.points_scale.insert(i + 1, 1.4)

                        self.draw_points()

                        # add curve points
                        self.curve_points.append([0, 0])
                        self.curve_points.append([0, 0])
                        self.fade_curve_points.append([0, 0])
                        self.fade_curve_points.append([0, 0])

                        self.calc_curve_points()
                        break

    # Mouse: left click motion
    def b1_motion(self, event):
        # move point
        if self.selected is not None and self.edit_mode:
            pos = self.map.get_click_pos(event)
            self.points[self.selected] = pos
            self.map.set_circle_pos(f"OP{self.selected}", pos[0], pos[1])

            self.calc_curve_points()

    # Mouse: Motion
    def motion(self, event):
        if self.scale_dis is not None and self.edit_mode:
            # calculate distance to point
            click_pos = self.map.get_click_pos(event)
            dis = sqrt((self.points[self.selected][0] - click_pos[0]) ** 2 + (
                    self.points[self.selected][1] - click_pos[1]) ** 2)

            # apply scale
            self.points_scale[self.selected] = dis / (self.scale_dis / self.start_scale)

            # calc outline
            self.calc_curve_points()

    # Key: s click
    def keypress_s(self, event):
        if self.selected is not None and self.scale_dis is None and self.edit_mode:
            # calculate distance to point
            click_pos = self.map.get_click_pos(event)
            self.scale_dis = sqrt((self.points[self.selected][0] - click_pos[0]) ** 2 + (
                    self.points[self.selected][1] - click_pos[1]) ** 2)
            # assign starting scale
            self.start_scale = self.points_scale[self.selected]

    # Key: s release
    def keyrelease_s(self, event):
        if self.edit_mode:
            # reset scale variables
            self.scale_dis = None
            self.start_scale = None

    # Key: delete / backspace pressed
    def delete(self, event):
        if self.selected is not None and len(self.points) >= 2 and self.edit_mode:
            # erase elements from screen
            self.map.clear_circle(f"OP{len(self.points) - 1}")
            self.map.clear_line(f"OCL{len(self.points) - 1}")
            self.map.clear_circle(f"OCP{len(self.curve_points) - 1}")
            self.map.clear_circle(f"OCP{len(self.curve_points) - 2}")

            # delete list entry's
            self.points.pop(self.selected)
            self.points_scale.pop(self.selected)
            self.selected = None

            # draw new arrangement
            self.draw_points()

            # update outline
            self.calc_curve_points()

    # calculate polygon outline
    def __calc_outline(self, mode: str):
        self.outline_points.clear()
        self.fade_outline_points.clear()
        # ready up for bezier calculation
        if mode == "outline":
            points = [self.curve_points[-1]] + self.curve_points + self.curve_points[0:3]
        else:
            points = [self.fade_curve_points[-1]] + self.fade_curve_points + self.fade_curve_points[0:3]

        for i in range(len(points) - 4):
            vector_points = [
                points[i + 1],
                self.__get_vector_points(points[i], points[i + 1], points[i + 2])[1],
                self.__get_vector_points(points[i + 1], points[i + 2], points[i + 3])[0],
                points[i + 2]
            ]

            # add bezier points to poly list
            for pos in self.__calc_bezier(vector_points):
                if mode == "outline":
                    self.outline_points.append(pos)
                else:
                    self.fade_outline_points.append(pos)

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
            return (p2[0] - p13_dis / dx * (p12_dis / 3), p2[1] - p13_dis / dx * (p12_dis / 3) * (dy / dx)), (
                p2[0] + p13_dis / dx * (p23_dis / 3), p2[1] + p13_dis / dx * (p23_dis / 3) * (dy / dx))
        else:
            return (p2[0] - p13_dis / dy * (p12_dis / 3) * (dx / dy), p2[1] - p13_dis / dy * (p12_dis / 3)), (
                p2[0] + p13_dis / dy * (p23_dis / 3) * (dx / dy), p2[1] + p13_dis / dy * (p23_dis / 3))

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

    # calculate dis to line segment
    @staticmethod
    def distance_to_line_segment(x, y, p1x, p1y, p2x, p2y):
        line_length = sqrt((p2y - p1y) ** 2 + (p2x - p1x) ** 2)

        dot_product = ((x - p1x) * (p2x - p1x) + (y - p1y) * (p2y - p1y)) / line_length
        dot_product = max(0, min(dot_product, line_length))

        projection_x = p1x + dot_product * (p2x - p1x) / line_length
        projection_y = p1y + dot_product * (p2y - p1y) / line_length

        distance = sqrt((x - projection_x) ** 2 + (y - projection_y) ** 2)

        return distance
