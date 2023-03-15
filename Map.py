import tkinter as tk
from tkinter.font import Font

from Advanced_Canvas import Advanced_Rectangle, Advanced_Text, Advanced_Circle, Advanced_Line, Advanced_Image
from Data_class import Data


class Map(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, zoom: float = 1.0):
        # map parameters
        self.canvas = canvas
        self.center = [x, y]
        self.zoom = zoom

        self.x_offset = 0
        self.y_offset = 0

        self.fev_background = False
        self.fev_foreground = False

        self.font = Font(family="Arial", size=12)

        # objects
        self.rectangles_info = {}
        self.rectangles = {}
        self.texts_info = {}
        self.texts = {}
        self.images_info = {}
        self.images = {}
        self.circles_info = {}
        self.circles = {}
        self.lines_info = {}
        self.lines = {}
        self.polygon_map_info = {}
        self.polygon_map = {}

        self.order = {}

        # screen center
        self.screen_center = [self.center[0]+self.x_offset, self.center[1]+self.y_offset]

        # zoom slider
        self.move_slider = False

        self.zoom_slider_pos = None
        self.zoom_lin = None
        self.zoom_but = None

        # origin button
        self.origin_but_pos = None
        self.origin_but = None
        self.origin_img = None

        # create origin grid
        self.add_line("X-axis", -50, 0, 50, 0, 1, (150, 150, 150))
        self.add_line("Y-axis", 0, -50, 0, 50, 1, (150, 150, 150))

    # add a square element
    def add_rectangle(self, name: str, x: int, y: int, width: int, height: int, outline: (int, int, int) = None, color: (int, int, int) = (0, 0, 0), radius: int = 6):
        assert name not in self.rectangles, "Name does already exist in the dictionary choose an other one"

        self.rectangles_info.update({name: [x, y, width, height, radius]})
        self.rectangles.update({name: Advanced_Rectangle(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), round(width*self.zoom), round(height*self.zoom), color if outline is None else outline, color, round(radius*self.zoom))})

        self.order.update({f"R:{name}": max(self.order.items(), key=lambda x: x[1])[1] + 1 if len(self.order) > 0 else 0})
        self.sort_order()

    # add a text element
    def add_text(self, name: str, x: int, y: int, text: str, color: (int, int, int) = (0, 0, 0), font: Font = None):
        assert name not in self.texts, "Name does already exist in the dictionary choose an other one"

        self.texts_info.update({name: [x, y]})
        self.texts.update({name: Advanced_Text(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), text, color, self.font if font is None else font)})

        self.order.update({f"T:{name}": max(self.order.items(), key=lambda x: x[1])[1] + 1 if len(self.order) > 0 else 0})
        self.sort_order()

    # add a image element
    def add_img(self, name: str, x: int, y: int, source: str = None, anchor: str = "nw"):
        assert name not in self.images, "Name does already exist in the dictionary choose an other one"

        self.images_info.update({name: [x, y]})
        self.images.update({name: Advanced_Image(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), source, anchor=anchor)})

        self.order.update({f"I:{name}": max(self.order.items(), key=lambda x: x[1])[1] + 1 if len(self.order) > 0 else 0})
        self.sort_order()

    # add circle element
    def add_circle(self, name: str, x: int, y: int, radius: int, outline: (int, int, int) = None, color: (int, int, int) = (0, 0, 0)):
        assert name not in self.circles, "Name does already exist in the dictionary choose an other one"

        self.circles_info.update({name: [x, y, radius]})
        self.circles.update({name: Advanced_Circle(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), round(radius*self.zoom), color if outline is None else outline, color)})

        self.order.update({f"C:{name}": max(self.order.items(), key=lambda x: x[1])[1] + 1 if len(self.order) > 0 else 0})
        self.sort_order()

    # add line element
    def add_line(self, name: str, x1: int, y1: int, x2: int, y2: int, width: int, color: (int, int, int) = (0, 0, 0), width_lock: bool = False):
        assert name not in self.lines, "Name does already exist in the dictionary choose an other one"

        self.lines_info.update({name: [x1, y1, x2, y2, width, width_lock]})
        self.lines.update({name: Advanced_Line(self.canvas, self.screen_center[0]+round(x1*self.zoom), self.screen_center[1]+round(y1*self.zoom), self.screen_center[0]+round(x2*self.zoom), self.screen_center[1]+round(y2*self.zoom), 1 if round(width*self.zoom) <= 1 else round(width*self.zoom), color)})

        self.order.update({f"L:{name}": max(self.order.items(), key=lambda x: x[1])[1] + 1 if len(self.order) > 0 else 0})
        self.sort_order()

    # add polygon map
    def add_polygon_map(self, name: str, x: int, y: int, box_size: float, shape: (int, int), colors):
        assert name not in self.polygon_map, f"Name does already exist in the dictionary choose an other one {name}"

        self.polygon_map_info.update({name: [x, y, box_size]})
        self.polygon_map.update({name: Data(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), box_size*self.zoom, shape, colors)})

        self.order.update({f"P:{name}": max(self.order.items(), key=lambda x: x[1])[1] + 1 if len(self.order) > 0 else 0})
        self.sort_order()

    # set rectangle pos
    def set_rectangle_pos(self, name: str, x: int, y: int):
        assert name in self.rectangles, "Name does not exist cant change position of a non existing object"

        self.rectangles_info[name][0], self.rectangles_info[name][1] = x, y
        self.rectangles[name].set_pos(self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom))
        self.sort_order()

    # set image pos
    def set_img_pos(self, name: str, x: int, y: int):
        assert name in self.images, "Name does not exist cant change position of a non existing object"

        self.images_info[name][0], self.images_info[name][1] = x, y
        self.images[name].set_pos(self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom))

    # set circle pos
    def set_circle_pos(self, name: str, x: int, y: int):
        assert name in self.circles, "Name does not exist cant change position of a non existing object"

        self.circles_info[name][0], self.circles_info[name][1] = x, y
        self.circles[name].set_pos(self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom))

    # set line pos
    def set_line_pos(self, name: str, x1: int, y1: int, x2: int, y2: int):
        assert name in self.lines, "Name does not exist cant change position of a non existing object"

        self.lines_info[name][0], self.lines_info[name][1], self.lines_info[name][2], self.lines_info[name][3] = x1, y1, x2, y2
        self.lines[name].set_pos(self.screen_center[0]+round(x1*self.zoom), self.screen_center[1]+round(y1*self.zoom), self.screen_center[0]+round(x2*self.zoom), self.screen_center[1]+round(y2*self.zoom))

    # set text pos
    def set_text_pos(self, name: str, x: int, y: int):
        assert name in self.texts, "Name does not exist cant change position of a non existing object"

        self.texts_info[name][0], self.texts_info[name][1] = x, y
        self.texts[name].set_pos(self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom))

    def set_polygon_map_pos(self, name: str, x: int, y: int):
        assert name in self.polygon_map, "Name does not exist cant change position of a non existing object"

        self.polygon_map_info[name][0], self.polygon_map_info[name][1] = x, y
        self.polygon_map[name].set_pos(self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom))

    # change Rectangle z pos
    def set_rectangle_z_pos(self, name: str, z: int):
        assert name in self.rectangles, "Name does not exist cant change z position of a non existing object"
        assert z < len(self.order), "z value is to big"

        old_z = self.order[f"R:{name}"]

        # change other z values
        if old_z < z:
            for key, value in list(self.order.items())[old_z + 1:z + 1]:
                self.order[key] -= 1
        if old_z > z:
            for key, value in list(self.order.items())[z + 1:old_z + 1]:
                self.order[key] += 1

        # set new z value
        self.order[f"R:{name}"] = z

        self.sort_order()

    # change Text z pos
    def set_text_z_pos(self, name: str, z: int):
        assert name in self.texts, "Name does not exist cant change z position of a non existing object"
        assert z < len(self.order), "z value is to big"

        old_z = self.order[f"T:{name}"]

        # change other z values
        if old_z < z:
            for key, value in list(self.order.items())[old_z + 1:z + 1]:
                self.order[key] -= 1
        if old_z > z:
            for key, value in list(self.order.items())[z:old_z]:
                self.order[key] += 1

        # set new z value
        self.order[f"T:{name}"] = z

        self.sort_order()

    # change image z pos
    def set_img_z_pos(self, name: str, z: int):
        assert name in self.images, "Name does not exist cant change z position of a non existing object"
        assert z < len(self.order), "z value is to big"

        old_z = self.order[f"I:{name}"]

        # change other z values
        if old_z < z:
            for key, value in list(self.order.items())[old_z + 1:z + 1]:
                self.order[key] -= 1
        if old_z > z:
            for key, value in list(self.order.items())[z:old_z]:
                self.order[key] += 1

        # set new z value
        self.order[f"I:{name}"] = z

        self.sort_order()

    # change circle z pos
    def set_circle_z_pos(self, name: str, z: int):
        assert name in self.circles, "Name does not exist cant change z position of a non existing object"
        assert z < len(self.order), "z value is to big"

        old_z = self.order[f"C:{name}"]

        # change other z values
        if old_z < z:
            for key, value in list(self.order.items())[old_z + 1:z + 1]:
                self.order[key] -= 1
        if old_z > z:
            for key, value in list(self.order.items())[z:old_z]:
                self.order[key] += 1

        # set new z value
        self.order[f"C:{name}"] = z

        self.sort_order()

    # change circle z pos
    def set_line_z_pos(self, name: str, z: int):
        assert name in self.lines, "Name does not exist cant change z position of a non existing object"
        assert z < len(self.order), "z value is to big"

        old_z = self.order[f"L:{name}"]

        # change other z values
        if old_z < z:
            for key, value in list(self.order.items())[old_z + 1:z + 1]:
                self.order[key] -= 1
        if old_z > z:
            for key, value in list(self.order.items())[z:old_z]:
                self.order[key] += 1

        # set new z value
        self.order[f"L:{name}"] = z

        self.sort_order()

    # change polygon map z pos
    def set_polygon_map_z_pos(self, name: str, z: int):
        assert name in self.polygon_map, "Name does not exist cant change z position of a non existing object"
        assert z < len(self.order), "z value is to big"

        old_z = self.order[f"P:{name}"]

        # change other z values
        if old_z < z:
            for key, value in list(self.order.items())[old_z + 1:z + 1]:
                self.order[key] -= 1
        if old_z > z:
            for key, value in list(self.order.items())[z:old_z]:
                self.order[key] += 1

        # set new z value
        self.order[f"P:{name}"] = z

        self.sort_order()
    
    # clear rectangle
    def clear_rectangle(self, name: str):
        assert name in self.rectangles, "name does not exist try an other one"
        
        # erase from screen
        self.rectangles[name].clear()
        
        # clear rectangle information
        self.rectangles.pop(name)
        self.rectangles_info.pop(name)
        
        # clear z pos
        self.order.pop(f"R:{name}")

    # clear text
    def clear_text(self, name: str):
        assert name in self.texts, "name does not exist try an other one"

        # erase from screen
        self.texts[name].clear()

        # clear rectangle information
        self.texts.pop(name)
        self.texts_info.pop(name)

        # clear z pos
        self.order.pop(f"T:{name}")

    # clear image
    def clear_image(self, name: str):
        assert name in self.images, "name does not exist try an other one"

        # erase from screen
        self.images[name].clear()

        # clear rectangle information
        self.images.pop(name)
        self.images_info.pop(name)

        # clear z pos
        self.order.pop(f"I:{name}")

    # clear circle
    def clear_circle(self, name: str):
        assert name in self.circles, "name does not exist try an other one"

        # erase from screen
        self.circles[name].clear()

        # clear rectangle information
        self.circles.pop(name)
        self.circles_info.pop(name)

        # clear z pos
        self.order.pop(f"C:{name}")

    # clear line
    def clear_line(self, name: str):
        assert name in self.lines, "name does not exist try an other one"

        # erase from screen
        self.lines[name].clear()

        # clear rectangle information
        self.lines.pop(name)
        self.lines_info.pop(name)

        # clear z pos
        self.order.pop(f"L:{name}")

    # clear polygon map
    def clear_polygon_map(self, name: str):
        assert name in self.polygon_map, "name does not exist try an other one"

        # erase from screen
        self.polygon_map[name].clear()

        # clear rectangle information
        self.polygon_map.pop(name)
        self.polygon_map_info.pop(name)

        # clear z pos
        self.order.pop(f"P:{name}")

    # check if circle with name exists
    def rectangle_exists(self, name: str) -> bool:
        return name in self.rectangles

    # check if circle with name exists
    def text_exists(self, name: str) -> bool:
        return name in self.texts

    # check if circle with name exists
    def img_exists(self, name: str) -> bool:
        return name in self.images

    # check if circle with name exists
    def circle_exists(self, name: str) -> bool:
        return name in self.circles

    # check if circle with name exists
    def line_exists(self, name: str) -> bool:
        return name in self.lines

    # check if polygon map exists
    def polygon_map_exists(self, name: str) -> bool:
        return name in self.polygon_map

    # lock line width
    def lock_line_width(self, name: str):
        self.lines_info[name][5] = True

    # unlock line width
    def unlock_line_width(self, name: str):
        self.lines_info[name][5] = False

    # sort order according to z value
    def sort_order(self):
        self.order = dict(sorted(self.order.items(), key=lambda x: x[1]))

        # update the z_pos layout
        if self.fev_background:
            self.set_to_background(True)

        elif self.fev_foreground:
            self.set_to_foreground(True)

    # add a zoom slider
    def add_zoom_slider(self, x: int, y: int):
        self.zoom_slider_pos = [x, y]

        self.zoom_lin = Advanced_Line(self.canvas, x, y, x+200, y, 1, (150, 150, 150))
        self.zoom_but = Advanced_Rectangle(self.canvas, x+round(self.zoom*100)-10 if self.zoom <= 2.1 else x+200, y-8, 5, 16, None, (69, 69, 69), 2)

    def set_zoom_slider_pos(self, x: int, y: int):
        assert self.zoom_slider_pos is not None, "Zoom slider has not been added jet"

        self.zoom_slider_pos = [x, y]

        self.zoom_lin.set_pos(x, y, x+200, y)
        self.zoom_but.set_pos(x+round(self.zoom*100)-10 if self.zoom <= 2.1 else x+200, y-8)

    # add origin button
    def add_origin_button(self, x: int, y: int):
        self.origin_but_pos = [x, y]

        self.origin_but = Advanced_Rectangle(self.canvas, x, y, 25, 25, None, (240, 240, 240), 2)
        self.origin_img = Advanced_Image(self.canvas, x+1, y+1, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\origin_icon.png")

    # change origin button pos
    def set_origin_button_pos(self, x: int, y: int):
        assert self.origin_but_pos is not None, "Origin button has not been added jet"

        self.origin_but_pos = [x, y]

        self.origin_but.set_pos(x, y)
        self.origin_img.set_pos(x+1, y+1)

    # draw
    def draw(self):
        # define iterator
        iterator = self.order.items()
        if self.fev_background:
            iterator = reversed(self.order.items())

        # loop through everything
        for key, value in iterator:
            if key[0] == "R":
                self.rectangles[key[2:]].draw()

            elif key[0] == "T":
                self.texts[key[2:]].draw()

            elif key[0] == "I":
                self.images[key[2:]].draw()

            elif key[0] == "C":
                self.circles[key[2:]].draw()

            elif key[0] == "L":
                self.lines[key[2:]].draw()

            elif key[0] == "P":
                self.polygon_map[key[2:]].draw()

        if self.origin_but_pos is not None:
            self.origin_but.draw()
            self.origin_img.draw()

        if self.zoom_slider_pos is not None:
            self.zoom_lin.draw()
            self.zoom_but.draw()

    # clear everything
    def clear_all(self):
        # clear rectangles
        for key, value in self.rectangles.copy().items():
            self.clear_rectangle(key)

        # clear texts
        for key, value in self.texts.copy().items():
            self.clear_text(key)

        # clear images
        for key, value in self.images.copy().items():
            self.clear_image(key)

        # clear circles
        for key, value in self.circles.copy().items():
            self.clear_circle(key)

        # clear lines
        for key, value in self.lines.copy().items():
            if key != "X-axis" and key != "Y-axis":
                self.clear_line(key)

        # clear polygon maps
        for key, value in self.polygon_map.copy().items():
            self.clear_polygon_map(key)

        self.polygon_map.clear()
        self.polygon_map_info.clear()

        # reset zoom/position
        self.add_offset(-self.x_offset, -self.y_offset, None, "b2")
        self.add_zoom(1-self.zoom)

    # set to background
    def set_to_background(self, forever: bool = False):
        for key, value in reversed(self.order.items()):
            if key[0] == "R":
                self.rectangles[key[2:]].set_to_background(forever=True if forever else False)

            elif key[0] == "T":
                self.texts[key[2:]].set_to_background(forever=True if forever else False)

            elif key[0] == "I":
                self.images[key[2:]].set_to_background(forever=True if forever else False)

            elif key[0] == "C":
                self.circles[key[2:]].set_to_background(forever=True if forever else False)

            elif key[0] == "L":
                self.lines[key[2:]].set_to_background(forever=True if forever else False)

            elif key[0] == "P":
                self.polygon_map[key[2:]].set_to_background(forever=True if forever else False)

        # set forever back/foreground
        self.fev_background = forever
        self.fev_foreground = False if forever else self.fev_foreground

    # set to foreground
    def set_to_foreground(self, forever: bool = False):
        for key, value in self.order.items():

            if key[0] == "R":
                self.rectangles[key[2:]].set_to_foregorund(forever=True if forever else False)

            elif key[0] == "T":
                self.texts[key[2:]].set_to_foregorund(forever=True if forever else False)

            elif key[0] == "I":
                self.images[key[2:]].set_to_foregorund(forever=True if forever else False)

            elif key[0] == "C":
                self.circles[key[2:]].set_to_foregorund(forever=True if forever else False)

            elif key[0] == "L":
                self.lines[key[2:]].set_to_foregorund(forever=True if forever else False)

            elif key[0] == "P":
                self.polygon_map[key[2:]].set_to_foreground(forever=True if forever else False)

        # set forever back/foreground
        self.fev_background = False if forever else self.fev_background
        self.fev_foreground = forever

    # set center point
    def set_center(self, x: int, y: int):
        delta = [x-self.center[0], y-self.center[1]]
        self.center = [x, y]

        self.screen_center = [self.center[0]+self.x_offset, self.center[1]+self.y_offset]

        # define iterator
        iterator = self.order.items()
        if self.fev_background:
            iterator = reversed(self.order.items())

        # loop through everything
        for key, value in iterator:

            if key[0] == "R":
                value = self.rectangles[key[2:]]
                self.rectangles[key[2:]].set_pos(value.x+delta[0], value.y+delta[1])

            elif key[0] == "T":
                value = self.texts[key[2:]]
                self.texts[key[2:]].set_pos(value.x+delta[0], value.y+delta[1])

            elif key[0] == "I":
                value = self.images[key[2:]]
                self.images[key[2:]].set_pos(value.x+delta[0], value.y+delta[1])

            elif key[0] == "C":
                value = self.circles[key[2:]]
                self.circles[key[2:]].set_pos(value.x+delta[0], value.y+delta[1])

            elif key[0] == "L":
                value = self.lines[key[2:]]
                self.lines[key[2:]].set_pos(value.x1+delta[0], value.y1+delta[1], value.x2+delta[0], value.y2+delta[1])

            elif key[0] == "P":
                value = self.polygon_map[key[2:]]
                self.polygon_map[key[2:]].set_pos(value.x+delta[0], value.y+delta[1])

    # add x, y offset
    def add_offset(self, x: int, y: int, event = None, key: str = "b1") -> bool:
        if not self.move_slider and key == "b2":
            self.x_offset += x
            self.y_offset += y

            self.screen_center = [self.center[0]+self.x_offset, self.center[1]+self.y_offset]

            # define iterator
            iterator = self.order.items()
            if self.fev_background:
                iterator = reversed(self.order.items())

            # loop through everything
            for key, value in iterator:

                if key[0] == "R":
                    value = self.rectangles[key[2:]]
                    self.rectangles[key[2:]].set_pos(value.x+x, value.y+y)

                elif key[0] == "T":
                    value = self.texts[key[2:]]
                    self.texts[key[2:]].set_pos(value.x+x, value.y+y)

                elif key[0] == "I":
                    value = self.images[key[2:]]
                    self.images[key[2:]].set_pos(value.x+x, value.y+y)

                elif key[0] == "C":
                    value = self.circles[key[2:]]
                    self.circles[key[2:]].set_pos(value.x+x, value.y+y)

                elif key[0] == "L":
                    value = self.lines[key[2:]]
                    self.lines[key[2:]].set_pos(value.x1+x, value.y1+y, value.x2+x, value.y2+y)

                elif key[0] == "P":
                    value = self.polygon_map[key[2:]]
                    self.polygon_map[key[2:]].set_pos(value.x+x, value.y+y)

            return True

        # move slider
        elif self.move_slider and event is not None:
            event.x -= 3

            # calculate new zoom
            new_zoom = (event.x-self.zoom_slider_pos[0])/100+0.1
            if event.x <= self.zoom_slider_pos[0]:
                new_zoom = 0.1
            elif event.x >= self.zoom_slider_pos[0]+200:
                new_zoom = 2.1

            # apply new zoom
            self.add_zoom(new_zoom-self.zoom)

            return True

        return False

    # change zoom
    def add_zoom(self, zoom: float):
        if self.zoom+zoom <= 0.1:
            zoom = 0.1-self.zoom

        self.zoom += zoom

        # define iterator
        iterator = self.order.items()
        if self.fev_background:
            iterator = reversed(self.order.items())

        # loop through everything
        for key, value in iterator:

            if key[0] == "R":
                value = self.rectangles[key[2:]]
                value.set_pos(self.rectangles_info[key[2:]][0]*self.zoom+self.screen_center[0], self.rectangles_info[key[2:]][1]*self.zoom+self.screen_center[1])
                value.set_size(self.rectangles_info[key[2:]][2]*self.zoom, self.rectangles_info[key[2:]][3]*self.zoom)
                value.set_corner_radius(round(self.rectangles_info[key[2:]][4]*self.zoom) if self.rectangles_info[key[2:]][4]*self.zoom > 1 else 0)

            elif key[0] == "T":
                value = self.texts[key[2:]]
                value.set_pos(self.texts_info[key[2:]][0]*self.zoom+self.screen_center[0], self.texts_info[key[2:]][1]*self.zoom+self.screen_center[1])

            elif key[0] == "I":
                value = self.images[key[2:]]
                value.set_pos(self.images_info[key[2:]][0]*self.zoom+self.screen_center[0], self.images_info[key[2:]][1]*self.zoom+self.screen_center[1])
                value.set_size(round(value.get_size()[0] * self.zoom), round(value.get_size()[1] * self.zoom))

            elif key[0] == "C":
                value = self.circles[key[2:]]
                value.set_pos(self.circles_info[key[2:]][0]*self.zoom+self.screen_center[0], self.circles_info[key[2:]][1]*self.zoom+self.screen_center[1])
                value.set_radius(self.circles_info[key[2:]][2]*self.zoom if self.circles_info[key[2:]][2]*self.zoom > 1 else 1)

            elif key[0] == "L":
                value = self.lines[key[2:]]
                value.set_pos(self.lines_info[key[2:]][0]*self.zoom+self.screen_center[0], self.lines_info[key[2:]][1]*self.zoom+self.screen_center[1],
                              self.lines_info[key[2:]][2]*self.zoom+self.screen_center[0], self.lines_info[key[2:]][3]*self.zoom+self.screen_center[1])
                if not self.lines_info[key[2:]][5]:
                    value.set_width(1 if round(self.lines_info[key[2:]][4]*self.zoom) <= 1 else round(self.lines_info[key[2:]][4]*self.zoom))
                else:
                    value.set_width(self.lines_info[key[2:]][4])

            elif key[0] == "P":
                value = self.polygon_map[key[2:]]
                value.set_pos(self.polygon_map_info[key[2:]][0]*self.zoom+self.screen_center[0], self.polygon_map_info[key[2:]][1]*self.zoom+self.screen_center[1])
                value.set_box_size(self.polygon_map_info[key[2:]][2]*self.zoom)

        self.zoom_but.set_pos(self.zoom_slider_pos[0]+round(self.zoom*100)-10 if self.zoom <= 2.1 else self.zoom_slider_pos[0]+200, self.zoom_slider_pos[1]-8)

    # return position on map for left click
    def get_click_pos(self, event, pos: (int, int) = None) -> (int, int):
        # from event
        if pos is None:
            return (event.x-self.center[0])/self.zoom-self.x_offset/self.zoom, (event.y-self.center[1])/self.zoom-self.y_offset/self.zoom
        # from position
        else:
            return (pos[0]-self.center[0])/self.zoom-self.x_offset/self.zoom, (pos[1]-self.center[1])/self.zoom-self.y_offset/self.zoom

    # left click
    def button_1(self, event):
        # origin button
        if self.origin_but is not None and self.origin_but.is_pressed(event):
            self.add_offset(-self.x_offset, -self.y_offset, event, "b2")
            return True

        # zoom slider
        elif self.zoom_but is not None and (self.zoom_but.is_pressed(event) or (self.zoom_slider_pos[0] <= event.x <= self.zoom_slider_pos[0]+200 and self.zoom_slider_pos[1]-8 <= event.y <= self.zoom_slider_pos[1]+8)):
            event.x -= 3
            self.move_slider = True
            self.add_zoom((event.x - self.zoom_slider_pos[0]) / 100 + 0.1 - self.zoom)
            return True

        return False

    # release left click
    def buttonrelease_1(self, event):
        self.move_slider = False
