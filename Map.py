import tkinter as tk
from tkinter.font import Font

from Advanced_Canvas import Advanced_Rectangle, Advanced_Text, Advanced_Image, Advanced_Circle, Advanced_Line


class Map(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, zoom: float = 1.0):
        # map parameters
        self.canvas = canvas
        self.center = [x, y]
        self.zoom = zoom

        self.x_offset = 0
        self.y_offset = 0

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

        # screen center
        self.screen_center = [self.center[0]+self.x_offset, self.center[1]+self.y_offset]

        # zoom slider
        self.move_slider = None

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

    # add a text element
    def add_text(self, name: str, x: int, y: int, text: str, color: (int, int, int) = (0, 0, 0), font: Font = None):
        assert name not in self.texts, "Name does already exist in the dictionary choose an other one"

        self.texts_info.update({name: [x, y]})
        self.texts.update({name: Advanced_Text(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), text, color, self.font if font is None else font)})

    # add a image element
    def add_img(self, name: str, x: int, y: int, source: str = None):
        assert name not in self.images, "Name does already exist in the dictionary choose an other one"

        self.images_info.update({name: [x, y]})
        self.images.update({name: Advanced_Image(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), source)})

    # add circle element
    def add_circle(self, name: str, x: int, y: int, radius: int, outline: (int, int, int) = None, color: (int, int, int) = (0, 0, 0)):
        assert name not in self.circles, "Name does already exist in the dictionary choose an other one"

        self.circles_info.update({name: [x, y, radius]})
        self.circles.update({name: Advanced_Circle(self.canvas, self.screen_center[0]+round(x*self.zoom), self.screen_center[1]+round(y*self.zoom), round(radius*self.zoom), color if outline is None else outline, color)})

    # add line element
    def add_line(self, name: str, x1: int, y1: int, x2: int, y2: int, width: int, color: (int, int, int) = (0, 0, 0)):
        assert name not in self.lines, "Name does already exist in the dictionary choose an other one"

        self.lines_info.update({name: [x1, y1, x2, y2, width]})
        self.lines.update({name: Advanced_Line(self.canvas, self.screen_center[0]+round(x1*self.zoom), self.screen_center[1]+round(y1*self.zoom), self.screen_center[0]+round(x2*self.zoom), self.screen_center[1]+round(y2*self.zoom), 1 if round(width*self.zoom) <= 1 else round(width*self.zoom), color)})

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
        for key, value in self.rectangles.items():
            value.draw()

        for key, value in self.texts.items():
            value.draw()

        for key, value in self.images.items():
            value.draw()

        for key, value in self.circles.items():
            value.draw()

        for key, value in self.lines.items():
            value.draw()

        if self.origin_but_pos is not None:
            self.origin_but.draw()
            self.origin_img.draw()

        if self.zoom_slider_pos is not None:
            self.zoom_lin.draw()
            self.zoom_but.draw()

    # set to background
    def set_to_background(self):
        for key, value in self.rectangles.items():
            value.set_to_background(forever=True)

        for key, value in self.texts.items():
            value.set_to_background(forever=True)

        for key, value in self.images.items():
            value.set_to_background(forever=True)

        for key, value in self.circles.items():
            value.set_to_background(forever=True)

        for key, value in self.lines.items():
            value.set_to_background(forever=True)

    # set center point
    def set_center(self, x: int, y: int):
        delta = [x-self.center[0], y-self.center[1]]
        self.center = [x, y]

        self.screen_center = [self.center[0]+self.x_offset, self.center[1]+self.y_offset]

        for key, value in self.rectangles.items():
            value.set_pos(value.x+delta[0], value.y+delta[1])

        for key, value in self.texts.items():
            value.set_pos(value.x+delta[0], value.y+delta[1])

        for key, value in self.images.items():
            value.set_pos(value.x+delta[0], value.y+delta[1])

        for key, value in self.circles.items():
            value.set_pos(value.x+delta[0], value.y+delta[1])

        for key, value in self.lines.items():
            value.set_pos(value.x1+delta[0], value.y1+delta[1], value.x2+delta[0], value.y2+delta[1])

    # add x, y offset
    def add_offset(self, x: int, y: int, event):
        if self.move_slider is None:
            self.x_offset += x
            self.y_offset += y

            self.screen_center = [self.center[0]+self.x_offset, self.center[1]+self.y_offset]

            for key, value in self.rectangles.items():
                value.set_pos(value.x+x, value.y+y)

            for key, value in self.texts.items():
                value.set_pos(value.x+x, value.y+y)

            for key, value in self.images.items():
                value.set_pos(value.x+x, value.y+y)

            for key, value in self.circles.items():
                value.set_pos(value.x+x, value.y+y)

            for key, value in self.lines.items():
                value.set_pos(value.x1+x, value.y1+y, value.x2+x, value.y2+y)

        else:
            if self.zoom_slider_pos[0] <= event.x <= self.zoom_slider_pos[0]+200:
                self.add_zoom(x/100)

    # change zoom
    def add_zoom(self, zoom: float):
        if self.zoom+zoom <= 0.1:
            zoom = 0.1-self.zoom

        self.zoom += zoom

        for key, value in self.rectangles.items():
            value.set_pos(self.rectangles_info[key][0]*self.zoom+self.screen_center[0], self.rectangles_info[key][1]*self.zoom+self.screen_center[1])

        for key, value in self.texts.items():
            value.set_pos(self.texts_info[key][0]*self.zoom+self.screen_center[0], self.texts_info[key][1]*self.zoom+self.screen_center[1])

        for key, value in self.images.items():
            value.set_pos(self.images_info[key][0]*self.zoom+self.screen_center[0], self.images_info[key][1]*self.zoom+self.screen_center[1])

        for key, value in self.circles.items():
            value.set_pos(self.circles_info[key][0]*self.zoom+self.screen_center[0], self.circles_info[key][1]*self.zoom+self.screen_center[1])

        for key, value in self.lines.items():
            value.set_pos(self.lines_info[key][0]*self.zoom+self.screen_center[0], self.lines_info[key][1]*self.zoom+self.screen_center[1],
                          self.lines_info[key][2]*self.zoom+self.screen_center[0], self.lines_info[key][3]*self.zoom+self.screen_center[1])
            value.set_width(1 if round(self.lines_info[key][4]*self.zoom) <= 1 else round(self.lines_info[key][4]*self.zoom))

        self.zoom_but.set_pos(self.zoom_slider_pos[0]+round(self.zoom*100)-10 if self.zoom <= 2.1 else self.zoom_slider_pos[0]+200, self.zoom_slider_pos[1]-8)

    # left click
    def button_1(self, event):
        # origin button
        if self.origin_but is not None and self.origin_but.is_pressed(event):
            self.add_offset(-self.x_offset, -self.y_offset, event)

        if self.zoom_but is not None and self.zoom_but.is_pressed(event):
            self.move_slider = event.x

    # release left click
    def buttonrelease_1(self, event):
        self.move_slider = None

