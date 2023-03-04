import tkinter as tk
import cv2
from PIL import Image, ImageTk, ImageDraw


class Special_Image(object):
    def __init__(self, canvas: tk.Canvas, x: int, y: int, src: str = None, anchor: str = "nw"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.src = src
        self.anchor = anchor

        self.object = None
        self.overlay = None
        self.overlay_img = None

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

        # get overlay width and height
        if self.overlay is not None:
            o_w, o_h = self.overlay_img.size
            o_height, o_width = round(height+abs(c_h-o_h)*(1/c_w*width)), round(width+abs(c_w-o_w)*(1/c_w*width))
            self.overlay = self.overlay_img.resize((o_width, o_height))

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

    # add overlaying image
    def add_overlay(self, img: Image):
        self.overlay_img = img
        self.overlay = self.overlay_img
        self.__update_tkimg()

        # update image
        if self.object is not None:
            self.canvas.itemconfigure(self.object, image=self.img)

            # update z layer pos
            self.__update_z_pos()

    # draw on overlay
    def draw_overlay(self, pos_x: int, pos_y: int, width: int, height: int, color: (int, int, int)):
        # draw on image
        draw = ImageDraw.Draw(self.overlay_img)
        draw.rectangle((pos_x, pos_y, pos_x+width, pos_y+height), fill=(color[0], color[1], color[2], 128))

        # copy overlay img over to overlay
        self.set_size(self.cv2_img.shape[1], self.cv2_img.shape[0])

        # update
        self.__update_tkimg()

        # change image
        if self.object is not None:
            self.canvas.itemconfigure(self.object, image=self.img)

            # update z layer pos
            self.__update_z_pos()

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
        if self.overlay is None:
            # convert origin image
            img = cv2.cvtColor(self.cv2_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img)
            self.img = ImageTk.PhotoImage(pil_img)
        else:
            # convert origin image
            img = cv2.cvtColor(self.cv2_img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img).convert('RGBA')
            # create composite
            composite = Image.new("RGBA", self.overlay.size, (0, 0, 0, 0))
            offset_x, offset_y = abs(self.overlay.size[1]-pil_img.size[1])//2, abs(self.overlay.size[0]-pil_img.size[0])//2
            composite.paste(pil_img, (offset_y, offset_x))
            # lay overlay on composite
            composite.alpha_composite(self.overlay)
            self.img = ImageTk.PhotoImage(composite)
