import tkinter as tk

class Polygon_Map(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int):
        self.canvas = canvas

        self.x = x
        self.y = y