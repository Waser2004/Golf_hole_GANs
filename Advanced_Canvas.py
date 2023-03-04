import tkinter as tk
from tkinter.font import Font
import cv2
from PIL import Image, ImageTk
from math import sqrt, ceil, pi, sin, cos, radians


class Advanced_Circle(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, radius: int, color: (int, int, int), outline: (int, int, int) = None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.r = radius
        self.ol = list(color) if outline is None else list(outline)
        self.c = list(color)

        self.object = None

        self.background = False
        self.foreground = False

    # draw circle on the screen
    def draw(self):
        if self.object is None:
            self.object = self.canvas.create_oval(self.x - self.r, self.y - self.r, self.x + self.r, self.y + self.r, outline=self.rgb_to_hex(self.ol), fill=self.rgb_to_hex(self.c))

        # update z layer pos
        self.__update_z_pos()

    # erase circle from the screen
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # change the position of the circle
    def set_pos(self, x: int, y: int):
        # set class parameters
        self.x = x
        self.y = y

        # change position
        if self.object is not None:
            self.canvas.coords(self.object, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
            self.canvas.tag_raise(self.object, tk.ALL)

            # update z layer pos
            self.__update_z_pos()

    # change radius
    def set_radius(self, radius: int):
        # set class parameter
        self.r = radius

        # change radius
        if self.object is not None:
            self.canvas.coords(self.object, self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r)
            self.canvas.tag_raise(self.object, tk.ALL)

            # update z layer pos
            self.__update_z_pos()

    # update color
    def set_color(self, color: (int, int, int), outline: (int, int, int) = None):
        # update class parameters
        self.c = color
        self.ol = color if outline is None else outline

        # change color
        if self.object is not None:
            self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c), outline=self.rgb_to_hex(self.ol))

            # update z layer pos
            self.__update_z_pos()

    # put into foreground
    def set_to_foreground(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_raise(self.object, tk.ALL)

        # update z layer state
        self.foreground = forever
        self.background = False if forever or self.background is False else True

    # set into the background
    def set_to_background(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_lower(self.object, tk.ALL)

        # update z layer state
        self.background = forever
        self.foreground = False if forever or self.foreground is False else True

    # check if it hase been pressed
    def is_pressed(self, event) -> bool:
        if sqrt((event.x - self.x)**2 + (event.y - self.y)**2) <= self.r:
            return True
        else:
            return False

    # update z position
    def __update_z_pos(self):
        # move to foreground
        if self.foreground:
            self.set_to_foreground(forever=True)
        # move to background
        elif self.background:
            self.set_to_background(forever=True)

    # convert rgb to hex
    @staticmethod
    def rgb_to_hex(rgb):
        assert all(0 <= color <= 255 for color in rgb), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


class Advanced_Line(object):
    def __init__(self, canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, width: int, color: (int, int, int)):
        self.canvas = canvas
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.w = width
        self.c = list(color)

        self.object = None

        self.background = False
        self.foreground = False

    # draw circle on the screen
    def draw(self):
        if self.object is None:
            self.object = self.canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill=self.rgb_to_hex(self.c), width=self.w)

        # update z layer pos
        self.__update_z_pos()

    # erase circle from the screen
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # change the position of the object
    def set_pos(self, x1: int = None, y1: int = None, x2: int = None, y2: int = None):
        # set class parameters
        self.x1 = x1 if x1 is not None else self.x1
        self.y1 = y1 if x1 is not None else self.y1
        self.x2 = x2 if x1 is not None else self.x2
        self.y2 = y2 if x1 is not None else self.y2

        # change position
        if self.object is not None:
            self.canvas.coords(self.object, self.x1, self.y1, self.x2, self.y2)
            self.canvas.tag_raise(self.object, tk.ALL)

            # update z layer pos
            self.__update_z_pos()

    def set_width(self, width: int):
        # set class parameter
        self.w = width

        # change width
        if self.object is not None:
            self.canvas.itemconfigure(self.object, width=self.w)

            # update z layer pos
            self.__update_z_pos()

    # update color
    def set_color(self, color: (int, int, int)):
        # set class parameter
        self.c = color

        # change color
        if self.object is not None:
            self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c))

            # update z layer pos
            self.__update_z_pos()

    # put into foreground
    def set_to_foreground(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_raise(self.object, tk.ALL)

        # update z layer state
        self.foreground = forever
        self.background = False if forever or self.background is False else True

    # set into the background
    def set_to_background(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_lower(self.object, tk.ALL)

        # update z layer state
        self.background = forever
        self.foreground = False if forever or self.foreground is False else True

    # update z position
    def __update_z_pos(self):
        # move to foreground
        if self.foreground:
            self.set_to_foreground(forever=True)
        # move to background
        elif self.background:
            self.set_to_background(forever=True)

    # convert rgb to hex
    @staticmethod
    def rgb_to_hex(rgb):
        assert all(0 <= color <= 255 for color in rgb), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


class Advanced_Text(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, text: str, color: (int, int, int), font: Font, anchor = None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.txt = text
        self.c = list(color)
        self.font = font
        self.anchor = tk.NW if anchor is None else anchor

        self.object = None

        self.foreground = False
        self.background = False

    # draw circle on the screen
    def draw(self):
        if self.object is None:
            self.object = self.canvas.create_text(self.x, self.y, text=self.txt, fill=self.rgb_to_hex(self.c), font=self.font, anchor=self.anchor)

        # update z layer pos
        self.__update_z_pos()

    # erase circle from the screen
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # change position
    def set_pos(self, x: int, y: int):
        # set class parameters
        self.x = x
        self.y = y

        # change position
        if self.object is not None:
            self.canvas.coords(self.object, self.x, self.y)
            self.canvas.tag_raise(self.object, tk.ALL)

            # update z layer pos
            self.__update_z_pos()

    # change text
    def set_text(self, text: str):
        # set class parameters
        self.txt = text

        # update text
        if self.object is not None:
            self.canvas.itemconfig(self.object, text=self.txt)
            self.canvas.tag_raise(self.object, tk.ALL)

        # update z layer pos
        self.__update_z_pos()

    # change color
    def set_color(self, color: (int, int, int)):
        # update class parameters
        self.c = color

        # update color
        if self.object is not None:
            self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c))

            # update z layer pos
            self.__update_z_pos()

    # change font
    def set_font(self, font: Font):
        # update class parameters
        self.font = font

        # update font
        if self.object is not None:
            self.canvas.itemconfig(self.object, font=self.font)

            # update z layer pos
            self.__update_z_pos()

    # change font
    def set_anchor(self, anchor):
        # update class parameters
        self.anchor = anchor

        # update anchor
        if self.object is not None:
            self.canvas.itemconfig(self.object, anchor=self.anchor)

            # update z layer pos
            self.__update_z_pos()

    # put into foreground
    def set_to_foreground(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_raise(self.object, tk.ALL)

        # update z layer state
        self.foreground = forever
        self.background = False if forever or self.background is False else True

    # set into the background
    def set_to_background(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_lower(self.object, tk.ALL)

        # update z layer state
        self.background = forever
        self.foreground = False if forever or self.foreground is False else True

    # update z position
    def __update_z_pos(self):
        # move to foreground
        if self.foreground:
            self.set_to_foreground(forever=True)
        # move to background
        elif self.background:
            self.set_to_background(forever=True)

    # convert rgb to hex
    @staticmethod
    def rgb_to_hex(rgb):
        assert all(0 <= color <= 255 for color in rgb), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


class Advanced_Rectangle(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int, outline: (int, int, int), color: (int, int, int) = None, radius: int = 0):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.o = list(color) if outline is None else list(outline)
        self.c = list(color)
        self.r = radius

        self.object = None
        self.update = False

        self.foreground = False
        self.background = False

    # draw square on the screen
    def draw(self):
        if self.update:
            self.clear()

        if self.object is None:
            # no edge radius
            if self.r < 1:
                self.object = self.canvas.create_rectangle(self.x, self.y, self.x+self.w, self.y+self.h, outline=self.rgb_to_hex(self.o), fill=self.rgb_to_hex(self.c))
            # add corner radius
            else:
                # calculate positions of the rounded corners
                length = self.r+1
                lines_nw = [[self.x+self.r-cos(radians(90/length*i))*self.r, self.y+self.r-sin(radians(90/length*i))*self.r] for i in range(length+1)]
                lines_ne = [[self.x+self.w-self.r+sin(radians(90/length*i))*self.r, self.y+self.r-cos(radians(90/length*i))*self.r] for i in range(length+1)]
                lines_se = [[self.x+self.w-self.r+cos(radians(90/length*i))*self.r, self.y+self.h-self.r+sin(radians(90/length*i))*self.r] for i in range(length+1)]
                lines_sw = [[self.x+self.r-sin(radians(90/length*i))*self.r, self.y+self.h-self.r+cos(radians(90/length*i))*self.r] for i in range(length+1)]

                self.object = self.canvas.create_polygon(lines_nw, lines_ne, lines_se, lines_sw, outline=self.rgb_to_hex(self.o), fill=self.rgb_to_hex(self.c))

        # update z layer pos
        self.__update_z_pos()

    # erase circle from the screen
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

            self.update = False

    # change position
    def set_pos(self, x: int, y: int, update: bool = True):
        # set class parameters
        self.x = x
        self.y = y

        # update location
        if update:
            self.update = True
            self.draw()

    # change size
    def set_size(self, width: int, height: int, update: bool = True):
        # update class parameters
        self.w = width
        self.h = height

        # update size
        if update:
            self.update = True
            self.draw()

    # change color
    def set_color(self, color: (int, int, int), outline: (int, int, int) = None):
        # update class parameters
        self.c = color
        self.o = color if outline is None else outline

        # update color
        if self.object is not None:
            self.canvas.itemconfig(self.object, fill=self.rgb_to_hex(self.c), outline=self.rgb_to_hex(self.o))

            # update z layer pos
            self.__update_z_pos()

    # change corner radius
    def set_corner_radius(self, radius: int, update: bool = True):
        # set class parameter
        self.r = radius

        # update corner radius
        if update:
            self.update = True
            self.draw()

    # check if it has been pressed
    def is_pressed(self, event) -> bool:
        if self.x <= event.x <= self.x + self.w and self.y <= event.y <= self.y + self.h:
            return True
        else:
            return False

    # put into foreground
    def set_to_foreground(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_raise(self.object, tk.ALL)

        # update z layer state
        self.foreground = forever
        self.background = False if forever or self.background is False else True

    # set into the background
    def set_to_background(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_lower(self.object, tk.ALL)

        # update z layer state
        self.background = forever
        self.foreground = False if forever or self.foreground is False else True

    # update z position
    def __update_z_pos(self):
        # move to foreground
        if self.foreground:
            self.set_to_foreground(forever=True)
        # move to background
        elif self.background:
            self.set_to_background(forever=True)

    # convert rgb to hex
    @staticmethod
    def rgb_to_hex(rgb):
        assert all(0 <= color <= 255 for color in rgb), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


class Advanced_Image(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, src: str = None, anchor: str = "nw"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.src = src
        self.anchor = anchor

        self.object = None

        self.foreground = False
        self.background = False

        if src is not None:
            # load image
            self.cv2_img = cv2.imread(self.src)
            self.__update_tkimg()

    # draw image
    def draw(self):
        # draw if it hasn't been drawn jet
        if self.object is None and self.src is not None:
            self.object = self.canvas.create_image(self.x, self.y, image=self.img, anchor=self.anchor)

        # update z layer pos
        self.__update_z_pos()

    # erase image
    def clear(self):
        if self.object is not None:
            self.canvas.delete(self.object)
            self.object = None

    # change position
    def set_pos(self, x, y):
        # set class parameters
        self.x = x
        self.y = y

        # change position
        if self.object is not None:
            self.canvas.coords(self.object, x, y)
            self.canvas.tag_raise(self.object, tk.ALL)

            # update z layer pos
            self.__update_z_pos()

    # change size
    def set_size(self, width: int, height: int = None):
        c_h, c_w = cv2.imread(self.src).shape[:2]
        height = width/(c_h/c_w) if height is None else height

        # change image size
        self.cv2_img = cv2.resize(cv2.imread(self.src), (width, height))
        self.__update_tkimg()

        # change image
        if self.object is not None:
            self.canvas.itemconfigure(self.object, image=self.img)

            # update z layer pos
            self.__update_z_pos()

    # change image
    def set_img(self, path: str):
        self.src = path

        # open image through open-cv
        self.cv2_img = cv2.imread(self.src)
        self.__update_tkimg()

        # update image
        if self.object is not None:
            self.canvas.itemconfigure(self.object, image=self.img)

            # update z layer pos
            self.__update_z_pos()

    # return size
    def get_size(self) -> (int, int):
        return cv2.imread(self.src).shape[:2][1], cv2.imread(self.src).shape[:2][0]

    # put into foreground
    def set_to_foreground(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_raise(self.object, tk.ALL)

        # update z layer state
        self.foreground = forever
        self.background = False if forever or self.background is False else True

    # set into the background
    def set_to_background(self, forever: bool = False):
        if self.object is not None:
            self.canvas.tag_lower(self.object, tk.ALL)

        # update z layer state
        self.background = forever
        self.foreground = False if forever or self.foreground is False else True

    # update z position
    def __update_z_pos(self):
        # move to foreground
        if self.foreground:
            self.set_to_foreground(forever=True)
        # move to background
        elif self.background:
            self.set_to_background(forever=True)

    # convert open-cv image to Tkinter img
    def __update_tkimg(self):
        img = cv2.cvtColor(self.cv2_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)
        self.img = ImageTk.PhotoImage(pil_img)


class Advanced_Entry(object):
    def __init__(self, root: tk.Tk, x: int, y: int, width: int, color: (int, int, int), font: Font):
        # set variables
        self.root = root
        self.x = x
        self.y = y
        self.w = width
        self.c = color
        self.font = font

        self.object = tk.Entry(self.root, bd=0, bg=self.rgb_to_hex(self.c), font=self.font)

    # draw entry
    def draw(self):
        if not self.object.winfo_ismapped():
            self.object.place(x=self.x, y=self.y, width=self.w)

    # erase entry
    def clear(self):
        if self.object.winfo_ismapped():
            self.object.place_forget()

    # change position
    def set_pos(self, x: int, y: int):
        # set class parameters
        self.x = x
        self.y = y

        # update pos
        if self.object.winfo_ismapped():
            self.object.place(x=self.x, y=self.y, width=self.w)

    # change width
    def set_width(self, width: int):
        # set class parameter
        self.w = width

        # change width
        if self.object.winfo_ismapped():
            self.object.configure(width=self.w)

    # change color
    def set_color(self, color: (int, int, int)):
        # set class parameter
        self.c = color

        # change color
        if self.object.winfo_ismapped():
            self.object.configure(bg=self.rgb_to_hex(self.c))

    # change font
    def set_font(self, font: Font):
        # set class parameter
        self.font = font

        # change font
        if self.object.winfo_ismapped():
            self.object.configure(font=font)

    # change text
    def set_text(self, txt: str):
        if self.object.winfo_ismapped():
            self.object.delete("0", "end")
            self.object.insert("0", txt)

    # return text
    def get_text(self) -> str:
        return self.object.get()

    # convert rgb to hex
    @staticmethod
    def rgb_to_hex(rgb):
        assert all(0 <= color <= 255 for color in rgb), "all rgb values have to be between 0 and 255"

        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
