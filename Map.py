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
        self.lines.update({name: Advanced_Line(self.canvas, self.screen_center[0]+round(x1*self.zoom), self.screen_center[1]+round(y1*self.zoom), self.screen_center[0]+round(x2*self.zoom), self.screen_center[1]+round(y2*self.zoom), round(width*self.zoom), color)})

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
    def add_offset(self, x: int, y: int):
        self.x_offset += x
        self.y_offset += y

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
