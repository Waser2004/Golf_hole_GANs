from tkinter import Canvas, CENTER, PhotoImage
from tkinter.font import Font
from math import *


class Circle(object):
    def __init__(self, canvas: Canvas, center: [int, int], radius: int, color: [int, int, int], outline_thickness: int,
                 outline_color: [int, int, int]):
        # assign variables
        self.canvas = canvas

        self.center = center
        self.radius = radius
        self.color = list(color)
        self.outline_thickness = outline_thickness
        self.outline_color = list(outline_color)

        # create object variable
        self.object = None

        # animation components
        self.animation_running = False
        self.animation_step = {
            "center": None,
            "radius": None,
            "color": None,
            "outline_thickness": None,
            "outline_color": None
        }
        self.animation_function = {
            "center": None,
            "radius": None,
            "color": None,
            "outline_thickness": None,
            "outline_color": None
        }

        self.animation_queue = {
            "center": [],
            "radius": [],
            "color": [],
            "outline_thickness": [],
            "outline_color": []
        }

    def draw(self):
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_oval(self.center[0] - self.radius, self.center[1] - self.radius,
                                                  self.center[0] + self.radius, self.center[1] + self.radius,
                                                  fill=self.__rgb_to_hex(self.color), outline=self.__rgb_to_hex(
                    self.outline_color) if self.outline_thickness >= 1 else None, width=self.outline_thickness)
        # update widget
        else:
            self.canvas.coords(self.object, self.center[0] - self.radius, self.center[1] - self.radius,
                               self.center[0] + self.radius, self.center[1] + self.radius)
            self.canvas.itemconfig(self.object, fill=self.__rgb_to_hex(self.color), outline=self.__rgb_to_hex(
                self.outline_color) if self.outline_thickness >= 1 else None, width=self.outline_thickness)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update center parameter
    def set_center(self, center: [int, int], animation: bool = False, animation_time: float = 1.0,
                   animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.center = center
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("center", self.center, center, animation_time,
                                     animation_type)

    # update radius parameter
    def set_radius(self, radius: int, animation: bool = False, animation_time: float = 1.0,
                   animation_type: str = "ease"):
        # update variable
        if not animation:
            self.radius = radius
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("radius", self.radius, radius, animation_time, animation_type)

    # update color parameter
    def set_color(self, color: [int, int, int], animation: bool = False, animation_time: float = 1.0,
                  animation_type: str = "ease"):
        # update variable
        if not animation:
            self.color = color
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("color", self.color, color, animation_time, animation_type)

    # update outline thickness parameter
    def set_outline_thickness(self, outline_thickness: int, animation: bool = False, animation_time: float = 1.0,
                              animation_type: str = "ease"):
        # update variable
        if not animation:
            self.outline_thickness = outline_thickness
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("outline_thickness", self.outline_thickness, outline_thickness, animation_time,
                                     animation_type)

    # update outline_color parameter
    def set_outline_color(self, outline_color: [int, int, int], animation: bool = False, animation_time: float = 1.0,
                          animation_type: str = "ease"):
        # update variable
        if not animation:
            self.outline_color = outline_color
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("outline_color", self.outline_color, outline_color, animation_time, animation_type)

    # check if it is pressed
    def is_pressed(self, x: int, y: int) -> bool:
        # is pressed
        if sqrt((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2) <= self.radius:
            return True
        # is not pressed
        return False

    # animate parameters
    def __animate_parameter(self, parameter_name: str, animation_start: float, animation_end: float,
                            animation_time: float, animation_type: str, force_start: bool = False):
        # convert animation parameters to list
        animation_start = [animation_start] if type(animation_start) != list else animation_start
        animation_end = [animation_end] if type(animation_end) != list else animation_end

        # set animation variables
        if self.animation_step[parameter_name] is not None:
            animation_start.clear()
            # load start value from queue
            if len(self.animation_queue[parameter_name]) > 0:
                for i, value in enumerate(self.animation_queue[parameter_name][-1][0]):
                    animation_start.append(value(self.animation_queue[parameter_name][-1][1]))
            # load start value from running animation
            else:
                for i, value in enumerate(self.animation_function[parameter_name]):
                    animation_start.append(value(self.animation_step[parameter_name][1]))

        animation_length = animation_time * 60
        animation_range = [end - start for start, end in zip(animation_start, animation_end)]

        # define animation functions
        animation_func = []
        for start, ran in zip(animation_start, animation_range):
            # ease
            if animation_type == "ease":
                animation_func.append(lambda step, start=start, ran=ran: (sin(step * (pi / animation_length) - (
                        pi / 2)) + 1) * ran / 2 + start)
            # constant
            else:
                animation_func.append(lambda step, start=start, ran=ran: step / animation_length * ran + start)

        # animation well be played immediately
        if self.animation_step[parameter_name] is None or force_start:
            self.animation_function[parameter_name] = animation_func
            self.animation_step[parameter_name] = [0, animation_length]

            if not self.animation_running:
                self.__animation_loop()
                self.animation_running = True
        # animation is set in to queue
        else:
            self.animation_queue[parameter_name].append((animation_func, animation_length))

    def __animation_loop(self):
        # update values
        for key, value in self.animation_step.items():
            if value is not None:
                # calculate new value
                new_value = []
                for i in self.animation_function[key]:
                    new_value.append(i(value[0] + 1))
                # set new value
                if len(new_value) == 1:
                    setattr(self, key, new_value[0])
                else:
                    setattr(self, key, new_value)
                # update step
                if value[0] + 1 < value[1]:
                    self.animation_step[key][0] = value[0] + 1
                else:
                    # new animation from queue
                    if len(self.animation_queue[key]) > 0:
                        self.animation_function[key] = self.animation_queue[key][0][0]
                        self.animation_step[key] = [0, self.animation_queue[key][0][1]]

                        self.animation_queue[key].pop(0)
                    # end animation
                    else:
                        self.animation_step[key] = None
                        self.animation_function[key] = None

        # update widget
        self.draw()

        # loop animation
        for key, value in self.animation_step.items():
            if value is not None:
                self.canvas.after(16, self.__animation_loop)
                break
        # stop loop if no more animations are running
        else:
            self.animation_running = False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))


class Rectangle(object):
    def __init__(self, canvas: Canvas, corner_1: [int, int], corner_2: [int, int], corner_radius: int,
                 color: [int, int, int], outline_thickness: int, outline_color: [int, int, int]):
        # assign variables
        self.canvas = canvas

        self.corner_1 = corner_1
        self.corner_2 = corner_2
        self.corner_radius = corner_radius
        self.color = list(color)
        self.outline_thickness = outline_thickness
        self.outline_color = list(outline_color)

        # create object variable
        self.object = None

        # animation components
        self.animation_running = False
        self.animation_step = {
            "corner_1": None,
            "corner_2": None,
            "corner_radius": None,
            "color": None,
            "outline_thickness": None,
            "outline_color": None
        }
        self.animation_function = {
            "corner_1": None,
            "corner_2": None,
            "corner_radius": None,
            "color": None,
            "outline_thickness": None,
            "outline_color": None
        }

        self.animation_queue = {
            "corner_1": [],
            "corner_2": [],
            "corner_radius": [],
            "color": [],
            "outline_thickness": [],
            "outline_color": []
        }

    def __calc_outline_points(self) -> list[[int, int]]:
        points = []
        # rectangle with no corner radius
        if self.corner_radius < 1:
            points += [self.corner_1[0], self.corner_1[1], self.corner_2[0], self.corner_1[1], self.corner_2[0],
                       self.corner_2[1], self.corner_1[0], self.corner_2[1]]
        # rectangle with corner radius
        else:
            # parameters
            if abs(self.corner_1[0] - self.corner_2[0]) / 2 > self.corner_radius and abs(
                    self.corner_1[1] - self.corner_2[1]) / 2 > self.corner_radius:
                corner_radius = self.corner_radius
            else:
                corner_radius = min(abs(self.corner_1[1] - self.corner_2[1]) / 2,
                                    abs(self.corner_1[1] - self.corner_2[1]) / 2)
            resolution = floor((pi * self.corner_radius) / 2)
            # top left corner
            center_1 = self.corner_1[0] + corner_radius, self.corner_1[1] + corner_radius
            for i in range(resolution + 1):
                points.append(center_1[0] + cos(pi + (pi / 2) / resolution * i) * corner_radius)
                points.append(center_1[1] + sin(pi + (pi / 2) / resolution * i) * corner_radius)
            # top right corner
            center_2 = self.corner_2[0] - corner_radius, self.corner_1[1] + corner_radius
            for i in range(resolution + 1):
                points.append(center_2[0] + cos((pi / 2) - (pi / 2) / resolution * i) * corner_radius)
                points.append(center_2[1] - sin((pi / 2) - (pi / 2) / resolution * i) * corner_radius)
            # bottom right corner
            center_3 = self.corner_2[0] - corner_radius, self.corner_2[1] - corner_radius
            for i in range(resolution + 1):
                points.append(center_3[0] + cos((2 * pi) + (pi / 2) / resolution * i) * corner_radius)
                points.append(center_3[1] + sin((2 * pi) + (pi / 2) / resolution * i) * corner_radius)
            # bottom left corner
            center_4 = self.corner_1[0] + corner_radius, self.corner_2[1] - corner_radius
            for i in range(resolution + 1):
                points.append(center_4[0] - cos((pi / 2) - (pi / 2) / resolution * i) * corner_radius)
                points.append(center_4[1] + sin((pi / 2) - (pi / 2) / resolution * i) * corner_radius)

        return points

    def draw(self):
        # calculate outline points
        points = self.__calc_outline_points()
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_polygon(points, fill=self.__rgb_to_hex(self.color),
                                                     outline=self.__rgb_to_hex(
                                                         self.outline_color) if self.outline_thickness >= 1 else None,
                                                     width=self.outline_thickness)
        # update widget
        else:
            self.canvas.coords(self.object, points)
            self.canvas.itemconfig(self.object, fill=self.__rgb_to_hex(self.color), outline=self.__rgb_to_hex(
                self.outline_color) if self.outline_thickness >= 1 else None, width=self.outline_thickness)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update rect position
    def set_pos(self, corner_1: [int, int], corner_2: [int, int], animation: bool = False, animation_time: float = 1.0,
                animation_type: str = "ease"):
        # update variables
        self.set_corner_1(corner_1, animation, animation_time, animation_type)
        self.set_corner_2(corner_2, animation, animation_time, animation_type)

    # update corner 1 parameter
    def set_corner_1(self, corner_1: [int, int], animation: bool = False, animation_time: float = 1.0,
                     animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.corner_1 = corner_1
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("corner_1", self.corner_1, corner_1, animation_time, animation_type)

    # update corner 2 parameter
    def set_corner_2(self, corner_2: [int, int], animation: bool = False, animation_time: float = 1.0,
                     animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.corner_2 = corner_2
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("corner_2", self.corner_2, corner_2, animation_time, animation_type)

    # update corner radius parameter
    def set_corner_radius(self, corner_radius: int, animation: bool = False, animation_time: float = 1.0,
                          animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.corner_radius = corner_radius
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("corner_radius", self.corner_radius, corner_radius, animation_time, animation_type)

    # update color parameter
    def set_color(self, color: [int, int, int], animation: bool = False, animation_time: float = 1.0,
                  animation_type: str = "ease"):
        # update variable
        if not animation:
            self.color = color
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("color", self.color, color, animation_time, animation_type)

    # update outline thickness parameter
    def set_outline_thickness(self, outline_thickness: int, animation: bool = False, animation_time: float = 1.0,
                              animation_type: str = "ease"):
        # update variable
        if not animation:
            self.outline_thickness = outline_thickness
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("outline_thickness", self.outline_thickness, outline_thickness, animation_time,
                                     animation_type)

    # update outline_color parameter
    def set_outline_color(self, outline_color: [int, int, int], animation: bool = False, animation_time: float = 1.0,
                          animation_type: str = "ease"):
        # update variable
        if not animation:
            self.outline_color = outline_color
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("outline_color", self.outline_color, outline_color, animation_time, animation_type)

    # check if it is pressed
    def is_pressed(self, x: int, y: int) -> bool:
        # is probably pressed
        if self.corner_1[0] <= x <= self.corner_2[0] and self.corner_1[1] <= y <= self.corner_2[1]:
            # no corner radius
            if self.corner_radius <= 1:
                return True
            # left side
            elif self.corner_1[0] <= x <= self.corner_1[0] + self.corner_radius:
                # click in top left corner
                if self.corner_1[1] <= y <= self.corner_1[1] + self.corner_radius:
                    center = [self.corner_1[0] + self.corner_radius, self.corner_1[1] + self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
                # click in bottom left corner
                elif self.corner_2[1] - self.corner_radius <= y <= self.corner_2[1]:
                    center = [self.corner_1[0] + self.corner_radius, self.corner_2[1] - self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
            # right side
            elif self.corner_2[0] <= x <= self.corner_2[0] + self.corner_radius:
                # click in top right corner
                if self.corner_1[1] <= y <= self.corner_1[1] + self.corner_radius:
                    center = [self.corner_1[0] + self.corner_radius, self.corner_2[1] - self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
                # click in bottom right corner
                elif self.corner_2[1] - self.corner_radius <= y <= self.corner_2[1]:
                    center = [self.corner_2[0] - self.corner_radius, self.corner_2[1] - self.corner_radius]
                    if sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2) <= self.corner_radius:
                        return True
                    return False
            # rest of the rectangle
            else:
                return True
        # is not pressed
        return False

    # animate parameters
    def __animate_parameter(self, parameter_name: str, animation_start: float, animation_end: float,
                            animation_time: float, animation_type: str, force_start: bool = False):
        # convert animation parameters to list
        animation_start = [animation_start] if type(animation_start) != list else animation_start
        animation_end = [animation_end] if type(animation_end) != list else animation_end

        # set animation variables
        if self.animation_step[parameter_name] is not None:
            animation_start.clear()
            # load start value from queue
            if len(self.animation_queue[parameter_name]) > 0:
                for i, value in enumerate(self.animation_queue[parameter_name][-1][0]):
                    animation_start.append(value(self.animation_queue[parameter_name][-1][1]))
            # load start value from running animation
            else:
                for i, value in enumerate(self.animation_function[parameter_name]):
                    animation_start.append(value(self.animation_step[parameter_name][1]))

        animation_length = animation_time * 60
        animation_range = [end - start for start, end in zip(animation_start, animation_end)]

        # define animation functions
        animation_func = []
        for start, ran in zip(animation_start, animation_range):
            # ease
            if animation_type == "ease":
                animation_func.append(lambda step, start=start, ran=ran: (sin(step * (pi / animation_length) - (
                        pi / 2)) + 1) * ran / 2 + start)
            # constant
            else:
                animation_func.append(lambda step, start=start, ran=ran: step / animation_length * ran + start)

        # animation well be played immediately
        if self.animation_step[parameter_name] is None or force_start:
            self.animation_function[parameter_name] = animation_func
            self.animation_step[parameter_name] = [0, animation_length]

            if not self.animation_running:
                self.__animation_loop()
                self.animation_running = True
        # animation is set in to queue
        else:
            self.animation_queue[parameter_name].append((animation_func, animation_length))

    def __animation_loop(self):
        # update values
        for key, value in self.animation_step.items():
            if value is not None:
                # calculate new value
                new_value = []
                for i in self.animation_function[key]:
                    new_value.append(i(value[0] + 1))
                # set new value
                if len(new_value) == 1:
                    setattr(self, key, new_value[0])
                else:
                    setattr(self, key, new_value)
                # update step
                if value[0] + 1 < value[1]:
                    self.animation_step[key][0] = value[0] + 1
                else:
                    # new animation from queue
                    if len(self.animation_queue[key]) > 0:
                        self.animation_function[key] = self.animation_queue[key][0][0]
                        self.animation_step[key] = [0, self.animation_queue[key][0][1]]

                        self.animation_queue[key].pop(0)
                    # end animation
                    else:
                        self.animation_step[key] = None
                        self.animation_function[key] = None

        # update widget
        self.draw()

        # loop animation
        for key, value in self.animation_step.items():
            if value is not None:
                self.canvas.after(16, self.__animation_loop)
                break
        # stop loop if no more animations are running
        else:
            self.animation_running = False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))


class Line(object):
    def __init__(self, canvas: Canvas, start: [int, int], end: [int, int], color: [int, int, int], thickness: int):
        # assign variables
        self.canvas = canvas

        self.start = start
        self.end = end
        self.color = list(color)
        self.thickness = thickness

        # create object variable
        self.object = None

        # animation components
        self.animation_running = False
        self.animation_step = {
            "start": None,
            "end": None,
            "color": None,
            "thickness": None,
        }
        self.animation_function = {
            "start": None,
            "end": None,
            "color": None,
            "thickness": None,
        }

        self.animation_queue = {
            "start": [],
            "end": [],
            "color": [],
            "thickness": [],
        }

    def draw(self):
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_line(self.start[0], self.start[1], self.end[0], self.end[1],
                                                  fill=self.__rgb_to_hex(self.color), width=self.thickness)
        # update widget
        else:
            self.canvas.coords(self.object, self.start[0], self.start[1], self.end[0], self.end[1])
            self.canvas.itemconfig(self.object, fill=self.__rgb_to_hex(self.color), width=self.thickness)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update position parameters
    def set_pos(self, start: [int, int], end: [int, int], animation: bool = False, animation_time: float = 1.0,
                animation_type: str = "ease"):
        # update variables
        if animation is False:
            self.start = start
            self.end = end
            self.draw()
        # animate variables
        else:
            self.__animate_parameter("start", self.start, start, animation_time, animation_type)
            self.__animate_parameter("end", self.end, end, animation_time, animation_type)

    # update start pos parameter
    def set_start_pos(self, start: [int, int], animation: bool = False, animation_time: float = 1.0,
                      animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.start = start
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("start", self.start, start, animation_time, animation_type)

    # update end pos parameter
    def set_end_pos(self, end: [int, int], animation: bool = False, animation_time: float = 1.0,
                    animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.end = end
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("end", self.end, end, animation_time, animation_type)

    # update color parameter
    def set_color(self, color: [int, int, int], animation: bool = False, animation_time: float = 1.0,
                  animation_type: str = "ease"):
        # update variable
        if not animation:
            self.color = color
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("color", self.color, color, animation_time, animation_type)

    # update thickness parameter
    def set_thickness(self, thickness: int, animation: bool = False, animation_time: float = 1.0,
                      animation_type: str = "ease"):
        # update variable
        if not animation:
            self.thickness = thickness
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("thickness", self.thickness, thickness, animation_time, animation_type)

    # animate parameters
    def __animate_parameter(self, parameter_name: str, animation_start: float, animation_end: float,
                            animation_time: float, animation_type: str, force_start: bool = False):
        # convert animation parameters to list
        animation_start = [animation_start] if type(animation_start) != list else animation_start
        animation_end = [animation_end] if type(animation_end) != list else animation_end

        # set animation variables
        if self.animation_step[parameter_name] is not None:
            animation_start.clear()
            # load start value from queue
            if len(self.animation_queue[parameter_name]) > 0:
                for i, value in enumerate(self.animation_queue[parameter_name][-1][0]):
                    animation_start.append(value(self.animation_queue[parameter_name][-1][1]))
            # load start value from running animation
            else:
                for i, value in enumerate(self.animation_function[parameter_name]):
                    animation_start.append(value(self.animation_step[parameter_name][1]))

        animation_length = animation_time * 60
        animation_range = [end - start for start, end in zip(animation_start, animation_end)]

        # define animation functions
        animation_func = []
        for start, ran in zip(animation_start, animation_range):
            # ease
            if animation_type == "ease":
                animation_func.append(lambda step, start=start, ran=ran: (sin(step * (pi / animation_length) - (
                        pi / 2)) + 1) * ran / 2 + start)
            # constant
            else:
                animation_func.append(lambda step, start=start, ran=ran: step / animation_length * ran + start)

        # animation well be played immediately
        if self.animation_step[parameter_name] is None or force_start:
            self.animation_function[parameter_name] = animation_func
            self.animation_step[parameter_name] = [0, animation_length]

            if not self.animation_running:
                self.__animation_loop()
                self.animation_running = True
        # animation is set in to queue
        else:
            self.animation_queue[parameter_name].append((animation_func, animation_length))

    def __animation_loop(self):
        # update values
        for key, value in self.animation_step.items():
            if value is not None:
                # calculate new value
                new_value = []
                for i in self.animation_function[key]:
                    new_value.append(i(value[0] + 1))
                # set new value
                if len(new_value) == 1:
                    setattr(self, key, new_value[0])
                else:
                    setattr(self, key, new_value)
                # update step
                if value[0] + 1 < value[1]:
                    self.animation_step[key][0] = value[0] + 1
                else:
                    # new animation from queue
                    if len(self.animation_queue[key]) > 0:
                        self.animation_function[key] = self.animation_queue[key][0][0]
                        self.animation_step[key] = [0, self.animation_queue[key][0][1]]

                        self.animation_queue[key].pop(0)
                    # end animation
                    else:
                        self.animation_step[key] = None
                        self.animation_function[key] = None

        # update widget
        self.draw()

        # loop animation
        for key, value in self.animation_step.items():
            if value is not None:
                self.canvas.after(16, self.__animation_loop)
                break
        # stop loop if no more animations are running
        else:
            self.animation_running = False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))


class Text(object):
    def __init__(self, canvas: Canvas, text: str, center: [int, int], color: [int, int, int], font_size: int = 15,
                 font_family: str = "arial", anchor=CENTER):
        # assign variables
        self.canvas = canvas

        self.text = text
        self.center = center
        self.color = list(color)
        self.font_size = font_size
        self.font_family = font_family
        self.anchor = anchor

        self.font = Font(family=self.font_family, size=-self.font_size)

        # create object variable
        self.object = None

        # animation components
        self.animation_running = False
        self.animation_step = {
            "center": None,
            "color": None,
            "font_size": None,
        }
        self.animation_function = {
            "center": None,
            "color": None,
            "font_size": None,
        }

        self.animation_queue = {
            "center": [],
            "color": [],
            "font_size": [],
        }

    def draw(self):
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_text(self.center[0], self.center[1], text=self.text, font=self.font,
                                                  fill=self.__rgb_to_hex(self.color), anchor=self.anchor)
        # update widget
        else:
            self.canvas.coords(self.object, self.center[0], self.center[1])
            self.canvas.itemconfig(self.object, text=self.text, font=self.font, fill=self.__rgb_to_hex(self.color),
                                   anchor=self.anchor)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update text parameter
    def set_text(self, text: str):
        # update variable
        self.text = text

        # draw on screen
        if self.object is not None:
            self.draw()

    # update center parameter
    def set_center(self, center: [int, int], animation: bool = False, animation_time: float = 1.0,
                   animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.center = center
            if self.object is not None:
                self.draw()
        # animate variable
        else:
            self.__animate_parameter("center", self.center, center, animation_time, animation_type)

    # update color parameter
    def set_color(self, color: [int, int, int], animation: bool = False, animation_time: float = 1.0,
                  animation_type: str = "ease"):
        # update variable
        if not animation:
            self.color = color
            if self.object is not None:
                self.draw()
        # animate variable
        else:
            self.__animate_parameter("color", self.color, color, animation_time, animation_type)

    # update font_size parameter
    def set_font_size(self, font_size: int, animation: bool = False, animation_time: float = 1.0,
                      animation_type: str = "ease"):
        # update variable
        if not animation:
            self.font_size = font_size
            self.font.configure(size=-self.font_size)
            if self.object is not None:
                self.draw()
        # animate variable
        else:
            self.__animate_parameter("font_size", self.font_size, font_size, animation_time, animation_type)

    # update font_family parameter
    def set_font_family(self, font_family: str):
        # update variable
        self.font_family = font_family
        self.font.configure(family=self.font_family)
        if self.object is not None:
            self.draw()

    # update anchor parameter
    def set_anchor(self, anchor):
        # update variable
        self.anchor = anchor
        if self.object is not None:
            self.draw()

    # animate parameters
    def __animate_parameter(self, parameter_name: str, animation_start: float, animation_end: float,
                            animation_time: float, animation_type: str, force_start: bool = False):
        # convert animation parameters to list
        animation_start = [animation_start] if type(animation_start) != list else animation_start
        animation_end = [animation_end] if type(animation_end) != list else animation_end

        # set animation variables
        if self.animation_step[parameter_name] is not None:
            animation_start.clear()
            # load start value from queue
            if len(self.animation_queue[parameter_name]) > 0:
                for i, value in enumerate(self.animation_queue[parameter_name][-1][0]):
                    animation_start.append(value(self.animation_queue[parameter_name][-1][1]))
            # load start value from running animation
            else:
                for i, value in enumerate(self.animation_function[parameter_name]):
                    animation_start.append(value(self.animation_step[parameter_name][1]))

        animation_length = animation_time * 60
        animation_range = [end - start for start, end in zip(animation_start, animation_end)]

        # define animation functions
        animation_func = []
        for start, ran in zip(animation_start, animation_range):
            # ease
            if animation_type == "ease":
                animation_func.append(lambda step, start=start, ran=ran: (sin(step * (pi / animation_length) - (
                        pi / 2)) + 1) * ran / 2 + start)
            # constant
            else:
                animation_func.append(lambda step, start=start, ran=ran: step / animation_length * ran + start)

        # animation well be played immediately
        if self.animation_step[parameter_name] is None or force_start:
            self.animation_function[parameter_name] = animation_func
            self.animation_step[parameter_name] = [0, animation_length]

            if not self.animation_running:
                self.__animation_loop()
                self.animation_running = True
        # animation is set in to queue
        else:
            self.animation_queue[parameter_name].append((animation_func, animation_length))

    def __animation_loop(self):
        # update values
        for key, value in self.animation_step.items():
            if value is not None:
                # calculate new value
                new_value = []
                for i in self.animation_function[key]:
                    new_value.append(i(value[0] + 1))
                # set new value
                if len(new_value) == 1:
                    setattr(self, key, new_value[0])
                else:
                    setattr(self, key, new_value)
                # update step
                if value[0] + 1 < value[1]:
                    self.animation_step[key][0] = value[0] + 1
                else:
                    # new animation from queue
                    if len(self.animation_queue[key]) > 0:
                        self.animation_function[key] = self.animation_queue[key][0][0]
                        self.animation_step[key] = [0, self.animation_queue[key][0][1]]

                        self.animation_queue[key].pop(0)
                    # end animation
                    else:
                        self.animation_step[key] = None
                        self.animation_function[key] = None

        # update widget
        self.font.configure(size=-round(self.font_size))
        if self.object is not None:
            self.draw()

        # loop animation
        for key, value in self.animation_step.items():
            if value is not None:
                self.canvas.after(16, self.__animation_loop)
                break
        # stop loop if no more animations are running
        else:
            self.animation_running = False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))


class Image(object):
    def __init__(self, canvas: Canvas, image: PhotoImage or None, center: [int, int], anchor=CENTER):
        # assign variables
        self.canvas = canvas

        self.image = image
        self.center = center
        self.anchor = anchor

        # create object variable
        self.object = None

        # animation components
        self.animation_running = False
        self.animation_step = {
            "center": None,
        }
        self.animation_function = {
            "center": None,
        }

        self.animation_queue = {
            "center": [],
        }

    def draw(self):
        # draw object on the screen if it has not already been drawn
        if self.object is None:
            self.object = self.canvas.create_image(self.center[0], self.center[1], image=self.image, anchor=self.anchor)
        # update widget
        else:
            self.canvas.coords(self.object, self.center[0], self.center[1])
            self.canvas.itemconfig(self.object, image=self.image, anchor=self.anchor)

    def delete(self):
        # erase object from the screen if it has been drawn before
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # update center parameter
    def set_center(self, center: [int, int], animation: bool = False, animation_time: float = 1.0,
                   animation_type: str = "ease"):
        # update variable
        if animation is False:
            self.center = center
            self.draw()
        # animate variable
        else:
            self.__animate_parameter("center", self.center, center, animation_time, animation_type)

    # update image parameter
    def set_image(self, image: PhotoImage):
        # update variable
        self.image = image
        self.draw()

    # update anchor parameter
    def set_anchor(self, anchor):
        # update variable
        self.anchor = anchor
        self.draw()

    # animate parameters
    def __animate_parameter(self, parameter_name: str, animation_start: float, animation_end: float,
                            animation_time: float, animation_type: str, force_start: bool = False):
        # convert animation parameters to list
        animation_start = [animation_start] if type(animation_start) != list else animation_start
        animation_end = [animation_end] if type(animation_end) != list else animation_end

        # set animation variables
        if self.animation_step[parameter_name] is not None:
            animation_start.clear()
            # load start value from queue
            if len(self.animation_queue[parameter_name]) > 0:
                for i, value in enumerate(self.animation_queue[parameter_name][-1][0]):
                    animation_start.append(value(self.animation_queue[parameter_name][-1][1]))
            # load start value from running animation
            else:
                for i, value in enumerate(self.animation_function[parameter_name]):
                    animation_start.append(value(self.animation_step[parameter_name][1]))

        animation_length = animation_time * 60
        animation_range = [end - start for start, end in zip(animation_start, animation_end)]

        # define animation functions
        animation_func = []
        for start, ran in zip(animation_start, animation_range):
            # ease
            if animation_type == "ease":
                animation_func.append(lambda step, start=start, ran=ran: (sin(step * (pi / animation_length) - (
                        pi / 2)) + 1) * ran / 2 + start)
            # constant
            else:
                animation_func.append(lambda step, start=start, ran=ran: step / animation_length * ran + start)

        # animation well be played immediately
        if self.animation_step[parameter_name] is None or force_start:
            self.animation_function[parameter_name] = animation_func
            self.animation_step[parameter_name] = [0, animation_length]

            if not self.animation_running:
                self.__animation_loop()
                self.animation_running = True
        # animation is set in to queue
        else:
            self.animation_queue[parameter_name].append((animation_func, animation_length))

    def __animation_loop(self):
        # update values
        for key, value in self.animation_step.items():
            if value is not None:
                # calculate new value
                new_value = []
                for i in self.animation_function[key]:
                    new_value.append(i(value[0] + 1))
                # set new value
                if len(new_value) == 1:
                    setattr(self, key, new_value[0])
                else:
                    setattr(self, key, new_value)
                # update step
                if value[0] + 1 < value[1]:
                    self.animation_step[key][0] = value[0] + 1
                else:
                    # new animation from queue
                    if len(self.animation_queue[key]) > 0:
                        self.animation_function[key] = self.animation_queue[key][0][0]
                        self.animation_step[key] = [0, self.animation_queue[key][0][1]]

                        self.animation_queue[key].pop(0)
                    # end animation
                    else:
                        self.animation_step[key] = None
                        self.animation_function[key] = None

        # update widget
        self.draw()

        # loop animation
        for key, value in self.animation_step.items():
            if value is not None:
                self.canvas.after(16, self.__animation_loop)
                break
        # stop loop if no more animations are running
        else:
            self.animation_running = False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))


class Polygon(object):
    def __init__(self, canvas: Canvas, points: list[[float, float]], color: [int, int, int], outline_thickness: int,
                 outline_color: [int, int, int]):
        # assign variables
        self.canvas = canvas

        self.points = points
        self.color = list(color)
        self.outline_thickness = outline_thickness
        self.outline_color = list(outline_color)

        # create object variable
        self.object = None

        # animation components
        self.animation_running = False
        self.animation_step = {
            "points": None,
            "color": None,
            "outline_thickness": None,
            "outline_color": None
        }
        self.animation_function = {
            "points": None,
            "color": None,
            "outline_thickness": None,
            "outline_color": None
        }

        self.animation_queue = {
            "points": [],
            "color": [],
            "outline_thickness": [],
            "outline_color": []
        }

    # draw
    def draw(self):
        # draw on canvas
        if self.object is None:
            self.object = self.canvas.create_polygon(self.points, fill=self.__rgb_to_hex(self.color),
                                                     width=self.outline_thickness,
                                                     outline=None if self.outline_thickness == 0 else self.__rgb_to_hex(
                                                         self.color))

    # animate parameters
    def __animate_parameter(self, parameter_name: str, animation_start: float, animation_end: float,
                            animation_time: float, animation_type: str, force_start: bool = False):
        # convert animation parameters to list
        animation_start = [animation_start] if type(animation_start) != list else animation_start
        animation_end = [animation_end] if type(animation_end) != list else animation_end

        # set animation variables
        if self.animation_step[parameter_name] is not None:
            animation_start.clear()
            # load start value from queue
            if len(self.animation_queue[parameter_name]) > 0:
                for i, value in enumerate(self.animation_queue[parameter_name][-1][0]):
                    animation_start.append(value(self.animation_queue[parameter_name][-1][1]))
            # load start value from running animation
            else:
                for i, value in enumerate(self.animation_function[parameter_name]):
                    animation_start.append(value(self.animation_step[parameter_name][1]))

        animation_length = animation_time * 60
        animation_range = [end - start for start, end in zip(animation_start, animation_end)]

        # define animation functions
        animation_func = []
        for start, ran in zip(animation_start, animation_range):
            # ease
            if animation_type == "ease":
                animation_func.append(lambda step, start=start, ran=ran: (sin(step * (pi / animation_length) - (
                        pi / 2)) + 1) * ran / 2 + start)
            # constant
            else:
                animation_func.append(lambda step, start=start, ran=ran: step / animation_length * ran + start)

        # animation well be played immediately
        if self.animation_step[parameter_name] is None or force_start:
            self.animation_function[parameter_name] = animation_func
            self.animation_step[parameter_name] = [0, animation_length]

            if not self.animation_running:
                self.__animation_loop()
                self.animation_running = True
        # animation is set in to queue
        else:
            self.animation_queue[parameter_name].append((animation_func, animation_length))

    def __animation_loop(self):
        # update values
        for key, value in self.animation_step.items():
            if value is not None:
                # calculate new value
                new_value = []
                for i in self.animation_function[key]:
                    new_value.append(i(value[0] + 1))
                # set new value
                if len(new_value) == 1:
                    setattr(self, key, new_value[0])
                else:
                    setattr(self, key, new_value)
                # update step
                if value[0] + 1 < value[1]:
                    self.animation_step[key][0] = value[0] + 1
                else:
                    # new animation from queue
                    if len(self.animation_queue[key]) > 0:
                        self.animation_function[key] = self.animation_queue[key][0][0]
                        self.animation_step[key] = [0, self.animation_queue[key][0][1]]

                        self.animation_queue[key].pop(0)
                    # end animation
                    else:
                        self.animation_step[key] = None
                        self.animation_function[key] = None

        # update widget
        self.draw()

        # loop animation
        for key, value in self.animation_step.items():
            if value is not None:
                self.canvas.after(16, self.__animation_loop)
                break
        # stop loop if no more animations are running
        else:
            self.animation_running = False

    @staticmethod
    def __rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(round(rgb[0]), round(rgb[1]), round(rgb[2]))
