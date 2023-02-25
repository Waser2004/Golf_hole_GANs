import tkinter as tk
from tkinter.font import Font
from math import sqrt, ceil, pi, sin, cos, radians


class Advanced_Circle(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, radius: int, outline: (int, int, int), color: (int, int, int)):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.r = radius
        self.ol = list(outline)
        self.c = list(color)

        self.scroll = 0

        self.object = None
        self.update = False

    # draw circle on the screen
    def draw(self):
        if self.update:
            self.clear()

        if self.object is None:
            self.object = self.canvas.create_oval(self.x - self.r, self.y - self.r+self.scroll, self.x + self.r, self.y + self.r+self.scroll, outline=self.rgb_to_hex(self.ol[0], self.ol[1], self.ol[2]), fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))

    # erase circle from the screen
    def clear(self):
        self.canvas.delete(self.object)
        self.object = None

        self.update = False

    # change the position of the circle
    def re_pos(self, x: int, y: int):
        # relocate circle
        if self.object is not None:
            self.canvas.coords(self.object, x - self.r, y - self.r+self.scroll, x + self.r, y + self.r+self.scroll)
            self.canvas.tag_raise(self.object, tk.ALL)

        # set class positions
        self.x = x
        self.y = y

    # update color
    def set_color(self, color: (int, int, int)):
        # update class color
        self.c = color

        # update color on screen
        self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))

    # update outline
    def set_outline(self, color: (int, int, int)):
        # update class color
        self.ol = color

        # update color on screen
        self.canvas.itemconfig(self.object, outline=self.rgb_to_hex(self.ol[0], self.ol[1], self.ol[2]))

    # check if it hase been pressed
    def is_pressed(self, event) -> bool:
        if sqrt((event.x - self.x)**2 + (event.y - (self.y+self.scroll))**2) <= self.r:
            return True
        else:
            return False

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int):
        assert all(0 <= color <= 255 for color in (r, g, b)), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Advanced_Line(object):
    def __init__(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, thickness: int, color: (int, int, int)):
        self.canvas = canvas
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.t = thickness
        self.c = list(color)

        self.scroll = 0

        self.object = None
        self.update = False

    # draw circle on the screen
    def draw(self):
        if self.update:
            self.clear()

        if self.object is None:
            self.object = self.canvas.create_line(self.x1, self.y1+self.scroll, self.x2, self.y2+self.scroll, fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]), width=self.t)

    # erase circle from the screen
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

            self.update = False

    # change the position of the object
    def re_pos(self, x1: int, y1: int, x2: int, y2: int):
        # change position on the screen
        if self.object is not None:
            self.canvas.coords(self.object, x1, y1+self.scroll, x2, y2+self.scroll)
            self.canvas.tag_raise(self.object, tk.ALL)

        # set class positions
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    # update color
    def set_color(self, color: (int, int, int)):
        # update class color
        self.c = color

        # update color on screen
        self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int):
        assert all(0 <= color <= 255 for color in (r, g, b)), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Advanced_Text(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, text: str, color: (int, int, int), font: Font, anchor = None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.txt = text
        self.c = list(color)
        self.font = font

        if anchor is None:
            self.anchor = tk.NW
        else:
            self.anchor = anchor

        self.scroll = 0

        self.object = None
        self.update = False

    # draw circle on the screen
    def draw(self):
        if self.update:
            self.clear()

        if self.object is None:
            self.object = self.canvas.create_text(self.x, self.y + self.scroll, text=self.txt, fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]), font=self.font, anchor=self.anchor)

    # erase circle from the screen
    def clear(self):
        self.canvas.delete(self.object)
        self.object = None

        self.update = False

    # change the position of the circle
    def re_pos(self, x: int, y: int):
        # change position on the screen
        if self.object is not None:
            self.canvas.coords(self.object, x, y+self.scroll)
            self.canvas.tag_raise(self.object, tk.ALL)

        # set class positions
        self.x = x
        self.y = y

    # update color
    def set_color(self, color: (int, int, int)):
        # update class color
        self.c = color

        # update color on screen
        self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))

    # set a new object
    def set_text(self, text: str):
        # update label on screen
        self.canvas.itemconfig(self.object, text=text)
        self.canvas.tag_raise(self.object, tk.ALL)

        # set class object
        self.txt = text

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int):
        assert all(0 <= color <= 255 for color in (r, g, b)), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Advanced_Square(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int, outline: (int, int, int), color: (int, int, int), radius: int = 0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.o = list(outline)
        self.c = list(color)
        self.r = radius

        self.scroll = 0

        self.object = None
        self.update = False

    # draw circle on the screen
    def draw(self):
        if self.update:
            self.clear()

        if self.object is None:
            # no edge radius
            if self.r < 1:
                self.object = self.canvas.create_rectangle(self.x, self.y+self.scroll, self.x + self.w, self.y + self.h, outline=self.rgb_to_hex(self.o[0], self.o[1], self.o[2]), fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))
            # add edge radius
            else:
                # calculate positions of the rounded edges
                length = self.r+1
                lines_nw = [[self.x+self.r-cos(radians(90/length*i))*self.r, self.y+self.r-sin(radians(90/length*i))*self.r+self.scroll] for i in range(length+1)]
                lines_ne = [[self.x+self.w-self.r+sin(radians(90/length*i))*self.r, self.y+self.r-cos(radians(90/length*i))*self.r+self.scroll] for i in range(length+1)]
                lines_se = [[self.x+self.w-self.r+cos(radians(90/length*i))*self.r, self.y+self.h-self.r+sin(radians(90/length*i))*self.r+self.scroll] for i in range(length+1)]
                lines_sw = [[self.x+self.r-sin(radians(90/length*i))*self.r, self.y+self.h-self.r+cos(radians(90/length*i))*self.r+self.scroll] for i in range(length+1)]

                self.object = self.canvas.create_polygon(lines_nw, lines_ne, lines_se, lines_sw, outline=self.rgb_to_hex(self.o[0], self.o[1], self.o[2]), fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))

    # erase circle from the screen
    def clear(self):
        self.canvas.delete(self.object)
        self.object = None

        self.update = False

    # change the position of the circle
    def re_pos(self, x: int, y: int, update: bool = True):
        # set class positions
        self.x = x
        self.y = y

        # update their location on the screen
        if update:
            self.update = True
            self.draw()

    # change height and width
    def re_size(self, width: int, height: int, update: bool = True):
        # update class width, height
        self.w = width
        self.h = height

        # update their location on the screen
        if update:
            self.update = True
            self.draw()

    # update color
    def set_color(self, color: (int, int, int)):
        # update class color
        self.c = color

        # update color on screen
        self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]))

    # update outline
    def set_outline(self, color: (int, int, int)):
        # update class color
        self.o = color

        # update color on screen
        self.canvas.itemconfig(self.object, outline=self.rgb_to_hex(self.o[0], self.o[1], self.o[2]))

    # check if it hase been pressed
    def is_pressed(self, event) -> bool:
        if self.x <= event.x <= self.x + self.w and self.y <= event.y <= self.y + self.h:
            return True
        else:
            return False

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int):
        assert all(0 <= color <= 255 for color in (r, g, b)), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Advanced_Entry(object):
    def __init__(self, root: tk.Tk, x: int, y: int, width: int, color: (int, int, int), font: Font):
        # set variables
        self.root = root
        self.x = x
        self.y = y
        self.w = width
        self.c = color
        self.font = font

        self.object = tk.Entry(self.root, bd=0, bg=self.rgb_to_hex(self.c[0], self.c[1], self.c[2]), font=self.font)
        self.update = False

    # draw entry on the screen
    def draw(self):
        # erase if updated
        if self.update:
            self.clear()

        # draw
        if not self.object.winfo_ismapped():
            self.object.place(x=self.x, y=self.y, width=self.w)

    # erase entry from the screen
    def clear(self):
        if self.object.winfo_ismapped():
            self.object.place_forget()

    # set new text that should be in the entry
    def set_text(self, txt: str):
        self.object.delete("0", "end")
        self.object.insert("0", txt)

    # reposition the entry on the screen
    def re_pos(self, x, y):
        self.x = x
        self.y = y

        self.object.place(x=self.x, y=self.y, width=self.w)

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int):
        assert all(0 <= color <= 255 for color in (r, g, b)), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(r, g, b)


class Advanced_Image(object):
    images = {}

    def __init__(self, canvas: tk.Canvas, x: int, y: int, src: str = None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.src = src

        self.object = None
        self.update = False

        if src is not None:
            self.img = tk.PhotoImage(file=self.src)
            self.images.update({self.src: self.img})

    def draw(self):
        # update the image if necessary
        if self.update:
            self.clear()
            self.update = False

        # draw if it hasn't been drawn jet
        if self.object is None and self.src is not None:
            self.object = self.canvas.create_image(self.x, self.y, image=self.img, anchor=tk.NW)

    # change the Image that should be visualised
    def change_img(self, path: str):
        img = tk.PhotoImage(file=path)
        self.src = path

        # check if the image is in the dict
        if self.src in self.images:
            self.img = self.images[self.src]
        # if it's not assign a new one
        else:
            self.images.update({self.src: img})

            self.img = self.images[self.src]

        # update the visualised image
        if self.object is not None:
            self.canvas.itemconfigure(self.object, image=self.img)

    # erase object from the screen
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # reposition the entry on the screen
    def re_pos(self, x, y):
        # change position on the screen
        if self.object is not None:
            self.canvas.coords(self.object, x, y)
            self.canvas.tag_raise(self.object, tk.ALL)

        # set class variables
        self.x = x
        self.y = y
