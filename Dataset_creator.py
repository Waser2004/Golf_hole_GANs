import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog

from Advanced_Canvas import Advanced_Square, Advanced_Text, Advanced_Image


class GUI(object):
    def __init__(self):
        # window_size
        self.WINDOW_SIZE = [500, 500]

        # create window
        self.root = tk.Tk()
        self.root.geometry(f"{self.WINDOW_SIZE[0]}x{self.WINDOW_SIZE[1]}")

        # create canvas
        self.canvas = tk.Canvas(self.root, width=self.WINDOW_SIZE[0], height=self.WINDOW_SIZE[0], bg="lightgray")
        self.canvas.place(x=-2, y=-2)

        # fonts
        self.F1 = Font(family="Arial", size=12)

        # initialise canvas objects
        self.sel_file_but = Advanced_Square(self.canvas, 0, 25, 200, 50, (240, 240, 240), (240, 240, 240), 6)
        self.sel_file_text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-75, 0, "Select file", (0, 0, 0), self.F1)

        self.Hole_IMG = Advanced_Image(self.canvas, 0, 0)

        # root bind events
        self.root.bind("<Button-1>", self.button_1)
        self.root.bind_class("Tk", "<Configure>", self.configure)

    # window loop
    def main(self):
        # draw canvas objects
        self.sel_file_but.draw()
        self.sel_file_text.draw()

        self.Hole_IMG.draw()

        self.root.after(27, self.main)

    # left click
    def button_1(self, event):
        if self.sel_file_but.is_pressed(event):
            # load Image
            file = filedialog.askopenfilename(initialdir="D:\\Golf_course_IMGs")

            if file != "":
                self.Hole_IMG.change_img(file)
                self.Hole_IMG.re_pos(self.WINDOW_SIZE[0]//2-self.Hole_IMG.img.width()//2, self.WINDOW_SIZE[1]//2-self.Hole_IMG.img.height()//2)
                self.Hole_IMG.img.subsample(2, 1)

    # configure event
    def configure(self, event):
        self.WINDOW_SIZE = [event.width, event.height]

        # resize canvas
        self.canvas.configure(width=self.WINDOW_SIZE[0], height=self.WINDOW_SIZE[1])

        # replace canvas objects
        self.sel_file_but.re_pos(self.WINDOW_SIZE[0]//2-100, self.sel_file_but.y)
        self.sel_file_text.re_pos(self.WINDOW_SIZE[0]//2-75, 75-self.F1.measure("linespace")//2)

        if self.Hole_IMG.src is not None:
            self.Hole_IMG.re_pos(self.WINDOW_SIZE[0]//2-self.Hole_IMG.img.width()//2, self.WINDOW_SIZE[1]//2-self.Hole_IMG.img.height()//2)

    # open the window
    def main_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
    gui.main_loop()
