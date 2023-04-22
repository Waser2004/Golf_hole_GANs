import tkinter as tk
from math import *
import copy

from Advanced_Canvas import Advanced_Circle, Advanced_Polygon, Advanced_Line, Advanced_Rectangle, Advanced_Image, Advanced_Lines


class Bezier_Map(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, colors: list[tuple[int, int, int]], map):
        # set class parameters
        self.canvas = canvas
        self.x = x
        self.y = y
        self.colors = colors
        self.map = map

        # polygon
        self.poly_index = None
        self.bezier_poly = []
        self.points_poly_map = []
        self.point_movement = False
        self.point_movement_offset = None
        self.point_movement_start = None

        self.sel_point = None

        # color
        self.cur_color = 0
        self.poly_colors = []

        # select polygon interface
        self.sel_map_pos = None
        self.sel_back = Advanced_Rectangle(self.canvas, 0, 0, 120, 24, None, (240, 240, 240), 2)
        self.sel_edit = Advanced_Image(self.canvas, 0, 0, "Icons\\edit.png", "center")
        self.sel_hide = Advanced_Image(self.canvas, 0, 0, "Icons\\hide.png", "center")
        self.sel_fade = Advanced_Image(self.canvas, 0, 0, "Icons\\gradient.png", "center")
        self.sel_up = Advanced_Image(self.canvas, 0, 0, "Icons\\up_arrow.png", "center")
        self.sel_down = Advanced_Image(self.canvas, 0, 0, "Icons\\down_arrow.png", "center")

        self.edit = False
        self.fade = False
        self.pre_adj_fade = None
        self.fade_mode = "add_fade"
        self.can_fade = []
        self.fade_index = None
        self.fade_index_start = False

        self.c_key_pressed = False
        self.circle_creation = False
        self.circle_center_point = None
        self.circle_radius = None

        self.fade_indicator = Advanced_Circle(self.canvas, 0, 0, 4, (0, 0, 0))

        # z order
        self.z_order = []
        self.background = False
        self.foreground = False

        # history handler
        self.history = []
        self.history_index = -1

        # --- canvas elements --- #
        self.can_bezier_points = []
        self.can_poly = []
        self.can_poly_arrow = Advanced_Line(self.canvas, 0, 0, 0, 0, 1, (0, 0, 0))

    # load data
    def load_data(self, bezier_points: list, fades: list, colors: list):
        # load data
        for i, val in enumerate(reversed(bezier_points)):
            self.recover_polygon(self.colors[colors[len(bezier_points)-1-i]], val, i, fades[len(bezier_points)-1-i])

        # unselect polygon
        self.unselect_polygon()

    # draw
    def draw(self):
        # draw select box
        if self.sel_map_pos is not None:
            self.sel_edit.draw()
            self.sel_hide.draw()
            self.sel_fade.draw()
            self.sel_up.draw()
            self.sel_down.draw()
            self.sel_back.draw()

        # draw bezier points
        if self.poly_index is not None:
            for obj in self.can_bezier_points[self.poly_index]:
                if self.edit is True:
                    obj.draw()

        # draw indication arrow
        if self.edit and len(self.can_bezier_points[self.poly_index]) > 1 and not self.circle_creation:
            self.can_poly_arrow.draw()

        # draw polygons
        for index in self.z_order:
            if not (self.poly_index == index and self.edit):
                # draw fade curves
                for fade in self.can_fade[index]:
                    fade[2].draw()

                # draw polygon
                self.can_poly[index].draw()

    # redo
    def redo(self):
        if self.history_index+1 < len(self.history):
            action = self.history[self.history_index+1]
            # new polygon was added
            if action[0] == "new_poly":
                self.create_new_poly(action[2][1], [action[2][0][0][0], action[2][0][0][1]])
            # circle was created
            elif action[0] == "cir_creation":
                print(action)
                self.create_circle(action[1], action[2], action[3])
                self.finish_circle_creation()
            # polygon was selected
            elif action[0] == "sel_poly":
                self.select_polygon(None, action[1])
            # edit mode was enabled
            elif action[0] == "edi_poly":
                self.edit_selected()
            # edit mode was disabled
            elif action[0] == "unedi_poly":
                self.edit_unselected()
            # polygon point was selected
            elif action[0] == "sel_point":
                self.select_point(action[2])
            # polygon point type was changed
            elif action[0] == "cha_point":
                self.change_type()
            # polygon point was moved
            elif action[0] == "mov_point":
                self.move_point(None, action[2])
            # polygon point was deleted
            elif action[0] == "del_point":
                self.delete_point()
            # polygon point was added
            elif action[0] == "add_point":
                self.add_point(None, action[1])
            # polygon was hidden
            elif action[0] == "hide_sel":
                self.hide_selected()
            # all polygons were hidden
            elif action[0] == "hide_all":
                self.hide_all()
            # selected polygon is being faded
            elif action[0] == "fade_poly":
                self.fade_selected()
            # fade line was added
            elif action[0] == "add_fade":
                self.add_fade(action[2], action[3], action[4])
            # fade line was adjusted
            elif action[0] == "adj_fade":
                self.adjust_fade(action[1], action[2], action[3], action[4])
            # fade line was deleted
            elif action[0] == "del_fade":
                self.delete_fade(action[1])
            # selected polygon is no longer being faded
            elif action[0] == "unfade_poly":
                self.fade_unselect()
            # polygon z_pos was raised
            elif action[0] == "up_z":
                self.up_z_pos()
            # polygon z_pos was lowered
            elif action[0] == "low_z":
                self.down_z_pos()
            # polygon was deleted
            elif action[0] == "del_poly":
                self.delete_polygon()
            # polygon was unselected
            elif action[0] == "uns_poly":
                self.unselect_polygon()

            self.history_index += 1

    # undo
    def undo(self):
        if self.history_index >= 0:
            action = self.history[self.history_index]
            # new polygon was added
            if action[0] == "new_poly":
                self.poly_index = action[1]
                self.delete_polygon()
            # circle was created
            elif action[0] == "cir_creation":
                self.delete_polygon()
            # polygon was selected
            elif action[0] == "sel_poly":
                self.unselect_polygon()
            # edit mode was enabled
            elif action[0] == "edi_poly":
                self.edit_unselected()
            # edit mode was disabled
            elif action[0] == "unedi_poly":
                self.edit_selected(action[1])
            # polygon point was selected
            elif action[0] == "sel_point":
                self.select_point(action[1])
            # polygon point type was changed
            elif action[0] == "cha_point":
                self.change_type()
            # polygon point was moved
            elif action[0] == "mov_point":
                self.move_point(None, action[1])
            # polygon point was deleted
            elif action[0] == "del_point":
                self.add_point(None, action[1])
            # polygon point was added
            elif action[0] == "add_point":
                self.delete_point()
            # polygon was hidden
            elif action[0] == "hide_sel":
                self.hide_selected()
            # all polygons were hidden
            elif action[0] == "hide_all":
                self.hide_all()
            # selected polygon is being faded
            elif action[0] == "fade_poly":
                self.fade_unselect()
            # fade line was added
            elif action[0] == "add_fade":
                self.delete_fade(action[1])
            # fade line was adjusted
            elif action[0] == "adj_fade":
                self.adjust_fade(action[1], action[5], action[6], action[7])
            # fade line was deleted
            elif action[0] == "del_fade":
                self.add_fade(action[2], action[3], action[4])
            # selected polygon is no longer being faded
            elif action[0] == "unfade_poly":
                self.fade_selected()
            # polygon z_pos was raised
            elif action[0] == "up_z":
                self.down_z_pos()
            # polygon z_pos was lowered
            elif action[0] == "low_z":
                self.up_z_pos()
            # polygon was deleted
            elif action[0] == "del_poly":
                self.recover_polygon(action[1], action[2], action[3], action[4])
            # polygon was unselected
            elif action[0] == "uns_poly":
                self.select_polygon(None, action[1])

            self.history_index -= 1

    # add history event
    def add_history(self, event_type: str, parameters: list):
        # clear upcoming events from list
        if self.history_index < len(self.history)-1:
            self.history[self.history_index+1:] = []
        # add event to list
        self.history.append([event_type] + parameters)
        self.history_index += 1

    # create new polygon
    def recover_polygon(self, color: (int, int, int), pos: list[[int, int], bool], z_value: int, fades: list[int, int, bool]):
        # create polygon
        self.poly_colors.append(color)
        # add map position to polygon
        self.poly_index = len(self.points_poly_map)
        self.points_poly_map.append([])
        self.can_bezier_points.append([])
        for p in pos:
            # add points map position
            self.points_poly_map[-1].append(p[0])
            # draw points on to the screen
            x, y = self.map.get_screen_pos(p[0])
            if p[1]:
                self.can_bezier_points[self.poly_index].append(Advanced_Rectangle(self.canvas, x-5, y-5, 10, 10, None, self.poly_colors[self.poly_index], 0))
            else:
                self.can_bezier_points[self.poly_index].append(Advanced_Circle(self.canvas, x, y, 5, self.poly_colors[self.poly_index]))

        self.bezier_poly.append([])

        # set z layer pos
        if self.background:
            for obj in self.can_bezier_points[self.poly_index]:
                obj.set_to_background(True)
        elif self.foreground:
            for obj in self.can_bezier_points[self.poly_index]:
                obj.set_to_foreground(True)

        # calc outline and select polygon
        poly_index = self.poly_index
        self.calc_outline(poly_index)
        self.select_polygon(None, poly_index)

        # add fade
        for fade in fades:
            # calculate curvature
            screen_pos = [self.map.get_screen_pos(pos) for pos in self.bezier_poly[self.poly_index]]
            # normal direction
            if not fade[2]:
                if fade[0] < fade[1]:
                    pos = screen_pos[fade[0]:fade[1]]
                else:
                    pos = screen_pos[fade[0]:] + screen_pos[:fade[1]]
            # revers direction
            else:
                if fade[0] > fade[1]:
                    pos = screen_pos[fade[1]:fade[0]]
                else:
                    pos = screen_pos[fade[1]:] + screen_pos[:fade[0]]

            self.can_fade[-1].append([fade[0], fade[1], Advanced_Lines(self.canvas, pos, 3, (0, 0, 0)), fade[2]])

            # set z layer pos
            if self.background:
                self.can_fade[-1][-1][2].set_to_background(True)
            elif self.foreground:
                self.can_fade[-1][-1][2].set_to_foreground(True)

        self.sel_point = len(pos)-1

        for i in range(self.z_order.index(self.poly_index)-z_value):
            self.up_z_pos()

    # recover polygon
    def create_new_poly(self, color: (int, int, int), pos: [int, int]):
        # convert pos if it is an event to map positions
        if type(pos) != list:
            pos = list(self.map.get_click_pos(pos))
        # create new polygon
        self.poly_colors.append(color)
        # add map position to polygon
        self.points_poly_map.append([[pos[0], pos[1]]])
        self.bezier_poly.append([])

        # update sel_bezier & poly_index
        self.poly_index = len(self.points_poly_map) - 1
        self.sel_point = 0
        self.edit = True

        x, y = self.map.get_screen_pos([pos[0], pos[1]])
        self.can_bezier_points.append([Advanced_Circle(self.canvas, x, y, 5, self.poly_colors[self.poly_index], (0, 0, 0))])

        # set z layer pos
        if self.background:
            self.can_bezier_points[self.poly_index][0].set_to_background(True)
        elif self.foreground:
            self.can_bezier_points[self.poly_index][0].set_to_foreground(True)

    # recover polygon
    def create_circle(self, color: (int, int, int), pos: [int, int], radius: int):
        # create new polygon
        self.poly_colors.append(color)
        # calculate points positions
        points = []
        number = ceil(radius*2*pi/15)
        for i in range(number):
            theta = 2 * pi * i / number
            x = int(pos[0] + radius * cos(theta))
            y = int(pos[1] + radius * sin(theta))
            points.append([x, y])

        # add map position to polygon
        self.points_poly_map.append(points)
        self.bezier_poly.append([])

        # update sel_bezier & poly_index
        self.poly_index = len(self.points_poly_map) - 1
        self.sel_point = None
        self.edit = True

        # draw points on screen
        self.can_bezier_points.append([])
        for p in points:
            x, y = self.map.get_screen_pos(p)
            self.can_bezier_points[self.poly_index].append(Advanced_Circle(self.canvas, x, y, 5, self.poly_colors[self.poly_index], None))

            # set z layer pos
            if self.background:
                self.can_bezier_points[self.poly_index][-1].set_to_background(True)
            elif self.foreground:
                self.can_bezier_points[self.poly_index][-1].set_to_foreground(True)

    # scale circle
    def scale_circle(self, event):
        if self.circle_creation:
            # calculate radius
            cursor_pos = self.map.get_click_pos(event)
            self.circle_radius = sqrt((self.circle_center_point[0]-cursor_pos[0])**2+(self.circle_center_point[1]-cursor_pos[1])**2)

            pos = self.circle_center_point
            
            # calculate points positions
            points = []
            number = ceil(self.circle_radius * 2 * pi / 15)
            for i in range(number):
                theta = 2 * pi * i / number
                x = int(pos[0] + self.circle_radius * cos(theta))
                y = int(pos[1] + self.circle_radius * sin(theta))
                points.append([x, y])
    
            # replace new points
            for i, p in enumerate(points):
                x, y = self.map.get_screen_pos(p)
                # replace point
                if len(self.can_bezier_points[self.poly_index]) > i:
                    self.can_bezier_points[self.poly_index][i].set_pos(x, y)
                    self.points_poly_map[self.poly_index][i] = p
                # create new point
                else:
                    self.can_bezier_points[self.poly_index].append(Advanced_Circle(self.canvas, x, y, 5, self.poly_colors[self.poly_index], None))
                    self.points_poly_map[self.poly_index].append(p)

                    # set z layer pos
                    if self.background:
                        self.can_bezier_points[self.poly_index][-1].set_to_background(True)
                    elif self.foreground:
                        self.can_bezier_points[self.poly_index][-1].set_to_foreground(True)

            # draw
            self.map.draw()
    
            # clear old points
            if len(points) < len(self.can_bezier_points[self.poly_index]):
                for _ in range(len(self.can_bezier_points[self.poly_index])-len(points)):
                    # clear points
                    self.can_bezier_points[self.poly_index][len(points)].clear()
                    self.can_bezier_points[self.poly_index].pop(len(points))
                    # clear points position
                    self.points_poly_map[self.poly_index].pop(len(points))

    # end the circle creation process
    def finish_circle_creation(self):
        # unselect edit mode
        self.edit_unselected()

        # reset variables
        self.circle_creation = False
        self.circle_center_point = None
        self.circle_radius = None

    # get information about circle
    def get_circle_information(self) -> list:
        return [self.poly_colors[self.poly_index], self.circle_center_point, self.circle_radius]

    # select polygon
    def select_polygon(self, event, index: int = None):
        polygon_index = None
        # according to click position
        if event is not None:
            indexes = []
            for i, obj in enumerate(self.can_poly):
                # check if polygon has been pressed
                if obj.is_pressed(event):
                    indexes.append(i)
            # find the polygon with the highest z_order
            for i, val in enumerate(self.z_order):
                if indexes.count(val):
                    # add edit bar
                    polygon_index = val
                    break
        # according to index
        else:
            polygon_index = index

        if polygon_index is not None:
            # calculate position for options box
            max_x, min_x = max(point[0] for point in self.bezier_poly[polygon_index]), min(point[0] for point in self.bezier_poly[polygon_index])
            min_y = min(point[1] for point in self.bezier_poly[polygon_index])
            self.sel_map_pos = [min_x + (max_x - min_x) / 2, min_y]
            self.set_sel_pos()
            # set index variables
            self.poly_index = polygon_index

    # add point
    def add_point(self, event, pos: [int, int] = None):
        # unselect prev point
        if self.sel_point is not None:
            self.can_bezier_points[self.poly_index][self.sel_point].set_color(self.poly_colors[self.poly_index])
        # add map position to polygon
        if pos is None:
            map_x, map_y = self.map.get_click_pos(event)
            screen_x, screen_y = event.x, event.y
        else:
            map_x, map_y = pos[0], pos[1]
            screen_x, screen_y = self.map.get_screen_pos(pos)

        self.points_poly_map[self.poly_index].insert(self.sel_point+1, [map_x, map_y])
        self.can_bezier_points[self.poly_index].insert(self.sel_point+1, Advanced_Circle(self.canvas, screen_x, screen_y, 5, self.poly_colors[self.poly_index], (0, 0, 0)))

        # set z layer pos
        if self.background:
            self.can_bezier_points[self.poly_index][self.sel_point+1].set_to_background(True)
        elif self.foreground:
            self.can_bezier_points[self.poly_index][self.sel_point+1].set_to_foreground(True)

        self.can_bezier_points[self.poly_index][self.sel_point+1].draw()
        self.select_point(self.sel_point + 1)

    # unselect fade
    def fade_unselect(self):
        if self.fade:
            if self.fade_mode == "add_fade" and self.fade_index is not None:
                self.can_fade[self.poly_index][self.fade_index][2].clear()
                self.can_fade[self.poly_index].pop(self.fade_index)
            # fade is being adjusted
            elif self.fade_mode == "adj_fade" and self.fade_index is not None:
                self.adjust_fade(self.pre_adj_fade[0], self.pre_adj_fade[1], self.pre_adj_fade[2], self.pre_adj_fade[3])

            # reset variables
            self.pre_adj_fade = None
            self.fade_index = None
            self.fade_index_start = False
            self.fade_mode = "add_fade"
            # unselect fade
            self.fade_indicator.clear()
            self.fade = False

            # select polygon
            self.select_polygon(None, self.poly_index)
    
    # add fade
    def add_fade(self, index_1: int, index_2: int, direction: bool):
        self.can_fade[self.poly_index].append([index_1, index_2+1, Advanced_Lines(self.canvas, self.can_poly[self.poly_index].pos[index_1-1:index_2+1], 3, (0, 0, 0)), direction])

        # calculate curvature
        fade = self.can_fade[self.poly_index][-1]
        screen_pos = [self.map.get_screen_pos(pos) for pos in self.bezier_poly[self.poly_index]]
        # normal direction
        if not fade[3]:
            if fade[0] < fade[1]:
                fade[2].set_pos(screen_pos[fade[0]:fade[1]])
            else:
                fade[2].set_pos(screen_pos[fade[0]:] + screen_pos[:fade[1]])
        # revers direction
        else:
            if fade[0] > fade[1]:
                fade[2].set_pos(screen_pos[fade[1]:fade[0]])
            else:
                fade[2].set_pos(screen_pos[fade[1]:] + screen_pos[:fade[0]])

        # set z layer pos
        if self.background:
            self.can_fade[self.poly_index][-1][2].set_to_background(True)
        elif self.foreground:
            self.can_fade[self.poly_index][-1][2].set_to_foreground(True)

    # adjust fade
    def adjust_fade(self, fade_index, index_1, index_2, direction):
        self.can_fade[self.poly_index][fade_index][2].clear()
        self.can_fade[self.poly_index][fade_index] = [index_1, index_2+1, Advanced_Lines(self.canvas, self.can_poly[self.poly_index].pos[index_1-1:index_2+1], 3, (0, 0, 0)), direction]

        # calculate curvature
        fade = self.can_fade[self.poly_index][fade_index]
        screen_pos = [self.map.get_screen_pos(pos) for pos in self.bezier_poly[self.poly_index]]
        # normal direction
        if not fade[3]:
            if fade[0] < fade[1]:
                fade[2].set_pos(screen_pos[fade[0]:fade[1]])
            else:
                fade[2].set_pos(screen_pos[fade[0]:]+screen_pos[:fade[1]])
        # revers direction
        else:
            if fade[0] > fade[1]:
                fade[2].set_pos(screen_pos[fade[1]:fade[0]])
            else:
                fade[2].set_pos(screen_pos[fade[1]:]+screen_pos[:fade[0]])

        # set z layer pos
        if self.background:
            self.can_fade[self.poly_index][-1][2].set_to_background(True)
        elif self.foreground:
            self.can_fade[self.poly_index][-1][2].set_to_foreground(True)
    
    # get fade info
    def get_fade_info(self, index: int = None):
        if index is None:
            index = self.fade_index
        
        return [index]+self.can_fade[self.poly_index][index][0:2]+[self.can_fade[self.poly_index][index][3]]

    # clear
    def clear(self):
        # polygon
        self.poly_index = None
        self.bezier_poly.clear()
        self.points_poly_map.clear()
        self.point_movement = False
        self.point_movement_offset = None
        self.point_movement_start = None

        self.sel_point = None

        # color
        self.cur_color = 0
        self.poly_colors.clear()

        # select polygon interface
        self.sel_map_pos = None
        self.sel_back.clear()
        self.sel_edit.clear()
        self.sel_hide.clear()
        self.sel_fade.clear()
        self.sel_up.clear()
        self.sel_down.clear()

        self.edit = False
        self.fade = False
        self.pre_adj_fade = None
        self.fade_mode = "add_fade"
        self.fade_index = None
        self.fade_index_start = False

        self.fade_indicator.clear()

        # z order
        self.z_order.clear()
        self.background = False
        self.foreground = False

        # history handler
        self.history.clear()
        self.history_index = -1

        # --- canvas elements --- #
        # fades
        for index in self.can_fade:
            for obj in index:
                obj[2].clear()
        self.can_fade.clear()
        # polygon points
        for index in self.can_bezier_points:
            for obj in index:
                obj.clear()
        self.can_bezier_points.clear()
        # polygons
        for obj in self.can_poly:
            obj.clear()
        self.can_poly.clear()
        # poly arrow
        self.can_poly_arrow.clear()

    # set to background
    def set_to_background(self, forever=False):
        # points
        for obj in self.can_bezier_points:
            obj.set_to_background(forever)

        # arrow
        self.can_poly_arrow.set_to_background(forever)

        # set sel box to background
        self.sel_edit.set_to_background(forever)
        self.sel_hide.set_to_background(forever)
        self.sel_fade.set_to_background(forever)
        self.sel_up.set_to_background(forever)
        self.sel_down.set_to_background(forever)
        self.sel_back.set_to_background(forever)

        self.background = forever
        self.foreground = self.foreground if not forever else False

    # set to background
    def set_to_foreground(self, forever=False):
        # points
        for obj in self.can_bezier_points:
            obj.set_to_foreground(forever)

        # arrow
        self.can_poly_arrow.set_to_foreground(forever)

        # set sel box to foreground
        self.sel_back.set_to_foreground(forever)
        self.sel_edit.set_to_foreground(forever)
        self.sel_hide.set_to_foreground(forever)
        self.sel_fade.set_to_foreground(forever)
        self.sel_up.set_to_foreground(forever)
        self.sel_down.set_to_foreground(forever)

        self.foreground = forever
        self.background = self.background if not forever else False

    # change select field position
    def set_sel_pos(self):
        if self.sel_map_pos is not None:
            # calculate screen pos
            screen_pos = self.map.get_screen_pos(self.sel_map_pos)

            # update positions
            self.sel_edit.set_pos(screen_pos[0]-48, screen_pos[1]-22)
            self.sel_hide.set_pos(screen_pos[0]-24, screen_pos[1]-22)
            self.sel_fade.set_pos(screen_pos[0], screen_pos[1]-22)
            self.sel_up.set_pos(screen_pos[0]+24, screen_pos[1]-22)
            self.sel_down.set_pos(screen_pos[0]+48, screen_pos[1]-22)
            self.sel_back.set_pos(screen_pos[0]-60, screen_pos[1]-34)

    # set position
    def set_pos(self, x: int, y: int):
        # change class parameters
        self.x, self.y = x, y

        # update sel box pos
        self.set_sel_pos()

        # update bezier points screen position
        if len(self.can_bezier_points) > 0:
            for i_list, lst in enumerate(self.can_bezier_points):
                for i_obj, obj in enumerate(lst):
                    b_x, b_y = self.map.get_screen_pos((self.points_poly_map[i_list][i_obj][0], self.points_poly_map[i_list][i_obj][1]))
                    # Circle
                    if type(obj) == Advanced_Circle:
                        obj.set_pos(b_x, b_y)
                    # Rectangle
                    else:
                        obj.set_pos(b_x-5, b_y-5, True if self.poly_index == i_list and self.edit else False)

        # update pos
        self.select_point(None)

        # update polygon screen_position
        if len(self.can_poly) > 0:
            for i, val in enumerate(self.z_order):
                screen_pos = [self.map.get_screen_pos(pos) for pos in self.bezier_poly[val]]
                # update fade curve positions
                for fade in self.can_fade[val]:
                    # normal direction
                    if not fade[3]:
                        if fade[0] < fade[1]:
                            fade[2].set_pos(screen_pos[fade[0]:fade[1]])
                        else:
                            fade[2].set_pos(screen_pos[fade[0]:]+screen_pos[:fade[1]])
                    # revers direction
                    else:
                        if fade[0] > fade[1]:
                            fade[2].set_pos(screen_pos[fade[1]:fade[0]])
                        else:
                            fade[2].set_pos(screen_pos[fade[1]:]+screen_pos[:fade[0]])
                # update polygon position
                self.can_poly[val].set_pos(screen_pos)

    # set zoom
    def set_zoom(self):
        self.set_pos(self.x, self.y)

    # delete fade curve
    def delete_fade(self, index: int = None):
        if self.fade_index is not None and index is None:
            index = self.fade_index

        # erase fade
        self.can_fade[self.poly_index][index][2].clear()
        self.can_fade[self.poly_index].pop(index)

        # update index
        self.fade_index = None

    # delete point
    def delete_point(self):
        # clear from screen
        self.can_bezier_points[self.poly_index][self.sel_point].clear()

        # clear from lists
        self.can_bezier_points[self.poly_index].pop(self.sel_point)
        self.points_poly_map[self.poly_index].pop(self.sel_point)

        # select previous point
        if len(self.can_bezier_points[self.poly_index]) > 0:
            self.select_point(self.sel_point-1 if self.sel_point-1 >= 0 else len(self.can_bezier_points[self.poly_index])-1)
        # delete polygon
        else:
            self.delete_polygon()

    # change point type
    def change_type(self):
        if self.poly_index is not None:
            self.can_bezier_points[self.poly_index][self.sel_point].clear()

            # change to angled point
            if type(self.can_bezier_points[self.poly_index][self.sel_point]) == Advanced_Circle:
                pos = (self.can_bezier_points[self.poly_index][self.sel_point].x, self.can_bezier_points[self.poly_index][self.sel_point].y)
                self.can_bezier_points[self.poly_index][self.sel_point] = Advanced_Rectangle(self.canvas, pos[0]-5, pos[1]-5, 10, 10, (0, 0, 0), self.poly_colors[self.poly_index])
            # change to curved point
            elif type(self.can_bezier_points[self.poly_index][self.sel_point]) == Advanced_Rectangle:
                pos = (self.can_bezier_points[self.poly_index][self.sel_point].x, self.can_bezier_points[self.poly_index][self.sel_point].y)
                self.can_bezier_points[self.poly_index][self.sel_point] = Advanced_Circle(self.canvas, pos[0]+5, pos[1]+5, 5, self.poly_colors[self.poly_index], (0, 0, 0))

    # button 1
    def button_1(self, event, color: int = None) -> bool:
        history_changed = False

        # create new polygon curve
        if self.poly_index is None and color is not None:
            # create a circle
            if self.c_key_pressed:
                # toggle circle creation
                self.circle_creation = True
                self.circle_center_point = list(self.map.get_click_pos(event))
                self.circle_radius = 3

                # create polygon
                self.create_circle(self.colors[color], self.circle_center_point, self.circle_radius)
            # create a normal polygon
            else:
                # create new polygon
                self.create_new_poly(self.colors[color], event)

                # add action to history
                self.add_history("new_poly", [self.poly_index, [self.points_poly_map[self.poly_index], self.poly_colors[self.poly_index]]])
                history_changed = True

        # select polygon curve
        elif self.poly_index is None and color is None:
            # select polygon
            self.select_polygon(event)

            # add event to history
            self.add_history("sel_poly", [self.poly_index])
            history_changed = True

        # add points to polygon curve
        else:
            # edit the bezier curve
            if self.edit:
                # check if point is selected
                for i, obj in enumerate(self.can_bezier_points[self.poly_index]):
                    # object is pressed
                    if obj.is_pressed(event):
                        self.can_bezier_points[self.poly_index][self.sel_point].set_color(self.poly_colors[self.poly_index])

                        # add to history
                        self.add_history("sel_point", [self.sel_point, i])
                        history_changed = True

                        self.select_point(i)

                        # enable point movement
                        self.point_movement = True
                        # calculate offset
                        click_pos = self.map.get_click_pos(event)
                        point_pos = self.points_poly_map[self.poly_index][self.sel_point]
                        self.point_movement_offset = [point_pos[0]-click_pos[0], point_pos[1]-click_pos[1]]
                        # set starting_pos
                        self.point_movement_start = [point_pos[0], point_pos[1]]

                        break
                else:
                    self.add_point(event)

                    # add to history
                    self.add_history("add_point", [self.points_poly_map[self.poly_index][self.sel_point]])
                    history_changed = True

            elif self.fade:
                mouse_pos = [event.x, event.y]

                # calculate nearest point to mouse
                distance = [-1, float("inf")]
                for i, point in enumerate(self.can_poly[self.poly_index].pos):
                    if sqrt((mouse_pos[0]-point[0])**2+(mouse_pos[1]-point[1])**2) < distance[1]:
                        distance = [i, sqrt((mouse_pos[0]-point[0])**2+(mouse_pos[1]-point[1])**2)]

                # add new fade curve
                if self.fade_index is None:
                    # check if old fade curve is being selected
                    for i, obj in enumerate(self.can_fade[self.poly_index]):
                        # starting point selected
                        if abs(obj[0]-distance[0]) < 10:
                            self.fade_index = i
                            self.fade_index_start = True

                            # update fade_mode
                            self.fade_mode = "adj_fade"
                            self.pre_adj_fade = self.get_fade_info()
                            break
                        # ending point selected
                        elif abs(obj[1]-distance[0]) < 10:
                            self.fade_index = i
                            self.fade_index_start = False

                            # update fade_mode
                            self.fade_mode = "adj_fade"
                            self.pre_adj_fade = self.get_fade_info()
                            break
                    # create new fade curve
                    else:
                        self.can_fade[self.poly_index].append([distance[0], distance[0]+1, Advanced_Lines(self.canvas, self.can_poly[self.poly_index].pos[distance[0]-1:distance[0]+1], 3, (0, 0, 0)), False])

                        # set z layer pos
                        if self.background:
                            self.can_fade[self.poly_index][-1][2].set_to_background(True)
                        elif self.foreground:
                            self.can_fade[self.poly_index][-1][2].set_to_foreground(True)

                        # update fade index / fade mode
                        self.fade_index = len(self.can_fade[self.poly_index])-1
                        self.fade_mode = "add_fade"

                # add fade ending point
                else:
                    # starting point
                    if self.fade_index_start:
                        self.can_fade[self.poly_index][self.fade_index][0] = distance[0]
                    # ending point
                    else:
                        self.can_fade[self.poly_index][self.fade_index][1] = distance[0]

                        # add add fade to history
                        if self.fade_mode == "add_fade":
                            self.add_history(self.fade_mode, self.get_fade_info())
                            history_changed = True

                    # add adjust fade to history
                    if self.fade_mode == "adj_fade":
                        self.add_history(self.fade_mode, [self.fade_index]+self.get_fade_info()[1:]+self.pre_adj_fade[1:])
                        self.pre_adj_fade = None
                        history_changed = True

                    # reset variables
                    self.fade_index = None
                    self.fade_index_start = False
                    self.fade_mode = "add_fade"

            # sel box is pressed
            elif self.sel_back.is_pressed(event):
                index = floor((event.x-self.sel_back.x)/24)
                # edit pressed
                if index == 0:
                    self.edit_selected()
                    # add to history
                    self.add_history("edi_poly", [])
                    history_changed = True
                # hide pressed
                elif index == 1:
                    # add to history
                    self.add_history("hide_sel", [])
                    history_changed = True

                    self.hide_selected()
                # add fade section
                elif index == 2:
                    self.fade_selected()
                    # add to history
                    self.add_history("fade_poly", [])
                    history_changed = True
                # up pressed
                elif index == 3:
                    self.up_z_pos()
                    # add to history
                    self.add_history("up_z", [])
                    history_changed = True
                # down pressed
                elif index == 4:
                    self.down_z_pos()
                    # add to history
                    self.add_history("low_z", [])
                    history_changed = True

        return history_changed

    # motion
    def motion(self, event):
        # get map position
        if self.poly_index is not None and len(self.can_poly) > self.poly_index and self.fade:
            mouse_pos = [event.x, event.y]

            distance = [-1, float(inf)]
            for i, point in enumerate(self.can_poly[self.poly_index].pos):
                if sqrt((mouse_pos[0]-point[0])**2+(mouse_pos[1]-point[1])**2) < distance[1]:
                    distance = [i, sqrt((mouse_pos[0]-point[0])**2+(mouse_pos[1]-point[1])**2)]

            self.fade_indicator.set_pos(self.can_poly[self.poly_index].pos[distance[0]][0], self.can_poly[self.poly_index].pos[distance[0]][1])
            self.fade_indicator.draw()

            if self.fade_index is not None:
                # change starting point
                if self.fade_index_start:
                    if abs(distance[0]-self.can_fade[self.poly_index][self.fade_index][1]) < 2:
                        if self.can_fade[self.poly_index][self.fade_index][1]+2 < len(self.can_poly[self.poly_index].pos):
                            distance[0] = self.can_fade[self.poly_index][self.fade_index][1]+2
                        else:
                            distance[0] = self.can_fade[self.poly_index][self.fade_index][1]-2

                    self.can_fade[self.poly_index][self.fade_index][0] = distance[0]
                # change ending point
                else:
                    if abs(distance[0]-self.can_fade[self.poly_index][self.fade_index][0]) < 2:
                        if self.can_fade[self.poly_index][self.fade_index][0]+2 < len(self.can_poly[self.poly_index].pos):
                            distance[0] = self.can_fade[self.poly_index][self.fade_index][0]+2
                        else:
                            distance[0] = self.can_fade[self.poly_index][self.fade_index][0]-2

                    self.can_fade[self.poly_index][self.fade_index][1] = distance[0]

                self.map.set_center(self.map.center[0], self.map.center[1])

    # move polygon point
    def move_point(self, event, pos: [int, int] = None):
        if pos is None:
            pos = self.map.get_click_pos(event)

        # update point_pos with offset
        if self.point_movement_offset is not None:
            self.points_poly_map[self.poly_index][self.sel_point][0] = pos[0]+self.point_movement_offset[0]
            self.points_poly_map[self.poly_index][self.sel_point][1] = pos[1]+self.point_movement_offset[1]
        # without offset
        else:
            self.points_poly_map[self.poly_index][self.sel_point][0] = pos[0]
            self.points_poly_map[self.poly_index][self.sel_point][1] = pos[1]

        # update pos
        self.map.set_center(self.map.center[0], self.map.center[1])

    def add_point_movement_history(self):
        # only add event if it has been moved
        if self.point_movement_start is not None:
            if self.poly_index is not None and self.sel_point is not None and self.points_poly_map[self.poly_index][self.sel_point] != self.point_movement_start:
                self.add_history("mov_point", [self.point_movement_start, copy.copy(self.points_poly_map[self.poly_index][self.sel_point])])

        # reset parameters
        self.point_movement_offset = None
        self.point_movement_start = None
        self.point_movement = False

    # fade selected
    def fade_selected(self):
        self.fade = True

        # erase sel box
        self.sel_map_pos = None
        self.sel_back.clear()
        self.sel_edit.clear()
        self.sel_fade.clear()
        self.sel_hide.clear()
        self.sel_up.clear()
        self.sel_down.clear()

    # change fade direction
    def change_fade_dir(self):
        # change dir
        if self.fade_index is not None and self.can_fade[self.poly_index][self.fade_index][3]:
            self.can_fade[self.poly_index][self.fade_index][3] = False
        elif self.fade_index is not None:
            self.can_fade[self.poly_index][self.fade_index][3] = True

        # update pos
        self.map.set_center(self.map.center[0], self.map.center[1])

    # edit unselected
    def edit_unselected(self):
        self.edit = False
        # erase components
        for obj in self.can_bezier_points[self.poly_index]:
            obj.clear()
        self.can_poly_arrow.clear()

        # delete polygon if not enough polygon points
        if len(self.can_bezier_points[self.poly_index]) < 3:
            self.delete_polygon()
        # draw polygon
        else:
            index = self.poly_index
            self.calc_outline(index)
            self.select_polygon(None, index)

    # edit selected
    def edit_selected(self, to_select_point: int = None):
        self.edit = True
        self.can_poly[self.poly_index].clear()

        # erase fade curves
        for obj in self.can_fade[self.poly_index]:
            obj[2].clear()

        # erase sel box
        self.sel_map_pos = None
        self.sel_back.clear()
        self.sel_edit.clear()
        self.sel_fade.clear()
        self.sel_hide.clear()
        self.sel_up.clear()
        self.sel_down.clear()

        if to_select_point is None:
            to_select_point = -1

        # select point
        self.select_point(to_select_point)

    # hide selected
    def hide_selected(self):
        if self.poly_index is not None:
            # clear polygon
            self.can_poly[self.poly_index].clear()
            # update to new type
            if type(self.can_poly[self.poly_index]) == Advanced_Polygon:
                self.can_poly[self.poly_index] = Advanced_Lines(self.canvas, [], 1, self.poly_colors[self.poly_index])
            elif type(self.can_poly[self.poly_index]) == Advanced_Lines:
                self.can_poly[self.poly_index] = Advanced_Polygon(self.canvas, [], self.poly_colors[self.poly_index], (0, 0, 0))

            # move to background
            if self.background:
                self.can_poly[self.poly_index].set_to_background(True)
            if self.foreground:
                self.can_poly[self.poly_index].set_to_foreground(True)

            # update_pos
            poly_index = self.poly_index
            self.calc_outline(self.poly_index)
            self.map.draw()

            # select polygon again
            self.select_polygon(None, poly_index)

    # move up in z
    def up_z_pos(self):
        if self.z_order.index(self.poly_index)-1 >= 0:
            index = self.z_order.index(self.poly_index)
            val = self.z_order.pop(index)
            self.z_order.insert(index-1, val)

        self.map.draw()

    # move down in z
    def down_z_pos(self):
        if self.z_order.index(self.poly_index)+1 < len(self.z_order):
            index = self.z_order.index(self.poly_index)
            val = self.z_order.pop(index)
            self.z_order.insert(index+1, val)

        self.map.draw()

    # hide all
    def hide_all(self):
        # count hidden polygons and unhidden polygons
        lines, polygons = 0, 0
        for obj in self.can_poly:
            if type(obj) == Advanced_Polygon:
                polygons += 1
            elif type(obj) == Advanced_Lines:
                lines += 1

        # hide / show polygons
        for i, obj in enumerate(self.can_poly):
            # hide all
            if lines <= polygons and type(obj) == Advanced_Polygon:
                # change class type
                self.can_poly[i].clear()
                self.can_poly[i] = Advanced_Lines(self.canvas, [], 1, self.poly_colors[i])

                # move to background
                if self.background:
                    self.can_poly[i].set_to_background(True)
                if self.foreground:
                    self.can_poly[i].set_to_foreground(True)

                # update_pos
                self.calc_outline(i)

            # show all
            elif lines > polygons and type(obj) == Advanced_Lines:
                # change class type
                self.can_poly[i].clear()
                self.can_poly[i] = Advanced_Polygon(self.canvas, [], self.poly_colors[i], (0, 0, 0))

                # move to background
                if self.background:
                    self.can_poly[i].set_to_background(True)
                if self.foreground:
                    self.can_poly[i].set_to_foreground(True)

                # update_pos
                self.calc_outline(i)

        # draw map
        self.map.draw()

    # select polygon point
    def select_point(self, index: int):
        if (self.sel_point is not None or index is not None) and self.poly_index is not None:
            index = self.sel_point if index is None else index

            # cut down index if needed
            if index > len(self.can_bezier_points[self.poly_index])-1:
                index = len(self.can_bezier_points[self.poly_index])-1

            # unselect old bezier point
            if self.sel_point is not None and len(self.can_bezier_points[self.poly_index]) > self.sel_point:
                self.can_bezier_points[self.poly_index][self.sel_point].set_color(self.poly_colors[self.poly_index])

            self.sel_point = index

            # calculate necessary cords
            next_index = index+1 if len(self.points_poly_map[self.poly_index]) > index+1 else 0
            dx = (self.points_poly_map[self.poly_index][next_index][0]-self.points_poly_map[self.poly_index][index][0])/3
            dy = (self.points_poly_map[self.poly_index][next_index][1]-self.points_poly_map[self.poly_index][index][1])/3

            p1 = self.map.get_screen_pos(self.points_poly_map[self.poly_index][index])
            p2 = self.map.get_screen_pos((self.points_poly_map[self.poly_index][index][0]+dx, self.points_poly_map[self.poly_index][index][1]+dy))

            # update border color
            self.can_bezier_points[self.poly_index][index].set_color(self.poly_colors[self.poly_index], (0, 0, 0))

            # update arrow position
            self.can_poly_arrow.set_pos(p1[0], p1[1], p2[0], p2[1])

    # get polygon information
    def get_poly_info(self, index=None):
        # set index
        if index is None:
            index = self.poly_index

        components = [self.poly_colors[index], [], self.z_order.index(index)]
        for i, obj in enumerate(self.points_poly_map[index]):
            components[1].append([[obj[0], obj[1]], True if type(self.can_bezier_points[index][i]) == Advanced_Rectangle else False])

        components.append([[f[0], f[1], f[3]] for f in self.can_fade[index]])

        return components

    # delete polygon
    def delete_polygon(self):
        # clear from screen
        for obj in self.can_bezier_points[self.poly_index]:
            obj.clear()
        # erase fade
        if len(self.can_poly) > self.poly_index:
            for obj in self.can_fade[self.poly_index]:
                obj[2].clear()
            # erase polygon
            self.can_poly[self.poly_index].clear()
            self.can_fade.pop(self.poly_index)
        # clear can_poly arrow
        self.can_poly_arrow.clear()

        # pop from list
        self.points_poly_map.pop(self.poly_index)
        self.poly_colors.pop(self.poly_index)
        self.bezier_poly.pop(self.poly_index)
        self.can_bezier_points.pop(self.poly_index)
        if len(self.can_poly) > self.poly_index:
            self.can_poly.pop(self.poly_index)
            # remove from z order
            self.z_order.remove(self.poly_index)

        # reorganise z_order
        for i, val in enumerate(self.z_order):
            if val > self.poly_index:
                self.z_order[i] -= 1

        # erase sel box
        self.sel_map_pos = None
        self.sel_back.clear()
        self.sel_edit.clear()
        self.sel_hide.clear()
        self.sel_fade.clear()
        self.sel_up.clear()
        self.sel_down.clear()

        # update edit/fade
        self.fade = False
        self.edit = False

        # set polygon/select index
        self.poly_index = None
        self.sel_point = None
        self.edit = False

    # unselect a polygon
    def unselect_polygon(self):
        # clear polygon points from screen
        for obj in self.can_bezier_points[self.poly_index]:
            obj.set_color(self.poly_colors[self.poly_index])
            obj.clear()

        # remove indication arrow
        self.can_poly_arrow.clear()

        # remove fade point
        self.fade_indicator.clear()
        if self.fade_index is not None:
            self.can_fade[self.poly_index][self.fade_index][2].clear()
            self.can_fade[self.poly_index].pop(self.fade_index)
            self.fade_index = None

        # erase sel box
        self.sel_map_pos = None
        self.sel_back.clear()
        self.sel_edit.clear()
        self.sel_hide.clear()
        self.sel_fade.clear()
        self.sel_up.clear()
        self.sel_down.clear()

        # update poly index
        self.poly_index = None
        self.fade = False
        self.edit = False

        self.map.set_center(self.map.center[0], self.map.center[1])

    def create_polygon(self):
        # delete polygon
        if len(self.can_bezier_points[self.poly_index]) < 3:
            self.delete_polygon()
        # create polygon
        else:
            self.calc_outline(self.poly_index)

    # prep for saving
    def prep_for_save(self):
        if self.poly_index is not None:
            # edit mode is selected
            if self.edit:
                self.edit_unselected()
            # fade mode is selected
            elif self.fade:
                self.fade_unselect()
            # unselect polygon
            self.unselect_polygon()

    # calculate polygon outline
    def calc_outline(self, poly_index: int):
        # ready up for bezier calculation
        points = [self.points_poly_map[poly_index][-1]]+self.points_poly_map[poly_index]+self.points_poly_map[poly_index][0:3]
        self.bezier_poly[poly_index].clear()

        for i in range(len(points)-4):
            # first point
            vector_points = [points[i + 1]]
            if type(self.can_bezier_points[poly_index][i]) == Advanced_Circle:
                vector_points.append(self.__get_vector_points(points[i], points[i+1], points[i+2])[1])
            # second point
            index = i+1 if len(self.can_bezier_points[poly_index]) > i+1 else 0
            if type(self.can_bezier_points[poly_index][index]) == Advanced_Circle:
                vector_points.append(self.__get_vector_points(points[i+1], points[i+2], points[i+3])[0])
            vector_points.append(points[i+2])

            # add bezier points to poly list
            for pos in self.__calc_bezier(vector_points):
                self.bezier_poly[poly_index].append(pos)

        # convert to screen post
        screen_pos = [self.map.get_screen_pos(pos) for pos in self.bezier_poly[poly_index]]
        # update bezier points on canvas
        if len(self.can_poly)-1 >= poly_index:
            self.can_poly[poly_index].set_pos(screen_pos)
        # create new canvas object
        else:
            self.can_poly.append(Advanced_Polygon(self.canvas, screen_pos, self.poly_colors[poly_index], (0, 0, 0)))
            self.can_fade.append([])

            # update z layer
            if self.background:
                self.can_poly[poly_index].set_to_background(True)
            if self.foreground:
                self.can_poly[poly_index].set_to_foreground(True)

            self.z_order.append(poly_index)
            self.map.draw()

        # unselect polygon
        if self.poly_index is not None:
            self.unselect_polygon()

    # get bezier vector points
    @staticmethod
    def __get_vector_points(p1: (int, int), p2: (int, int), p3: (int, int)) -> [(int, int), (int, int)]:
        # calculate delta x/y
        dx, dy = p3[0]-p1[0], p3[1]-p1[1]
        # calculate distances
        p13_dis = sqrt((p3[0]-p1[0])**2+(p3[1]-p1[1])**2)
        p12_dis = sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)
        p23_dis = sqrt((p3[0]-p2[0])**2+(p3[1]-p2[1])**2)

        # return vector points
        if abs(dx) >= abs(dy):
            return (p2[0]-p13_dis/dx*(p12_dis/3), p2[1]-p13_dis/dx*(p12_dis/3)*(dy/dx)), (p2[0]+p13_dis/dx*(p23_dis/3), p2[1]+p13_dis/dx*(p23_dis/3)*(dy/dx))
        else:
            return (p2[0]-p13_dis/dy*(p12_dis/3)*(dx/dy), p2[1]-p13_dis/dy*(p12_dis/3)), (p2[0]+p13_dis/dy*(p23_dis/3)*(dx/dy), p2[1]+p13_dis/dy*(p23_dis/3))

    # calculate bezier curve
    @staticmethod
    def __calc_bezier(points: list[tuple[int, int]]) -> list[(int, int)]:
        res = round(sqrt((points[-1][0]-points[0][0])**2+(points[-1][1]-points[0][1])**2))
        n = len(points)-1
        curve_points = []
        for i in range(res):
            t = i/(res-1) if res-1 > 0 else 1
            point = [0, 0]
            for j in range(n+1):
                cof = comb(n, j)*t**j*(1-t)**(n-j)
                point[0] += cof*points[j][0]
                point[1] += cof*points[j][1]
            curve_points.append(tuple(point))
        return curve_points
