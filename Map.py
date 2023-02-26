import tkinter as tk
from tkinter.font import Font

from Advanced_Canvas import Advanced_Rectangle, Advanced_Text, Advanced_Image, Advanced_Circle, Advanced_Line


class Map(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, zoom: float = 1.0):
        # map parameters
        self.canvas = canvas
        self.center = [x, y]
        self.zoom = zoom

        self.font = Font(family="Arial", size=12)

        # objects
        self.rectangles = {}
        self.texts = {}
        self.images = {}
        self.circles = {}
        self.lines = {}

    # add a square element
    def add_square(self, name: str, x: int, y: int, width: int, height: int, outline: (int, int, int) = None, color: (int, int, int) = (0, 0, 0), radius: int = 6):
        assert name in self.rectangles, "Name does already exist in the dictionary choose an other one"

        self.rectangles.update({name: Advanced_Rectangle(self.canvas, self.center[0] + x, self.center[1] + y, width, height, outline, color, radius)})

    # add a text element
    def add_text(self, name: str, x: int, y: int, text: str, color: (int, int, int) = (0, 0, 0), font: Font = None):
        assert name in self.texts, "Name does already exist in the dictionary choose an other one"

        self.texts.update({name: Advanced_Text(self.canvas, self.center[0]+x, self.center[1]+y, text, color, self.font if font is None else font)})

    # add a image element
    def add_img(self, name: str, x: int, y: int, source: str = None):
        assert name in self.images, "Name does already exist in the dictionary choose an other one"

        self.images.update({name: Advanced_Image(self.canvas, self.center[0]+x, self.center[1]+y, source)})

    # add circle element
    def add_circle(self, name: str, x: int, y: int, radius: int, outline: (int, int, int) = None, color: (int, int, int) = (0, 0, 0)):
        assert name in self.circles, "Name does already exist in the dictionary choose an other one"

        self.circles.update({name: Advanced_Circle(self.canvas, self.center[0]+x, self.center[1]+y, radius, outline, color)})

    # add line element
    def add_line(self, name: str, x1: int, y1: int, x2: int, y2: int, width: int, color: (int, int, int) = (0, 0, 0)):
        assert name in self.lines, "Name does already exist in the dictionary choose an other one"

        self.lines.update({name: Advanced_Line(self.canvas, self.center[0]+x1, self.center[1]+y1, self.center[0]+x2, self.center[1]+y2, width, color)})
