import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog

from Advanced_Canvas import Advanced_Rectangle, Advanced_Text, Advanced_Image, Advanced_Circle


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

        # playground parameters
        self.offset = [0, 0]
        self.zoom = 1

        # initialise canvas objects
        self.Hole_IMG = Advanced_Image(self.canvas, 0, 0)

        self.sel_file_but = Advanced_Rectangle(self.canvas, 0, 25, 200, 50, (240, 240, 240), (240, 240, 240), 6)
        self.sel_file_text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-75, 0, "Select file", (0, 0, 0), self.F1)

        self.action_but = Advanced_Rectangle(self.canvas, 0, 25, 200, 50, (240, 240, 240), (240, 240, 240), 6)
        self.action_text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-75, 0, "Select file", (150, 150, 150), self.F1)

        self.start_point = Advanced_Circle(self.canvas, -5, -5, 5, (255, 255, 255), (255, 255, 255))

        # root bind events
        self.root.bind("<Button-1>", self.button_1)
        self.root.bind("<MouseWheel>", self.scroll)
        self.root.bind_class("Tk", "<Configure>", self.configure)

    # window loop
    def main(self):
        # draw canvas objects
        self.Hole_IMG.draw()

        self.sel_file_but.draw()
        self.sel_file_text.draw()

        self.action_but.draw()
        self.action_text.draw()

        self.start_point.draw()

        self.root.after(27, self.main)

    # left click
    def button_1(self, event):
        if self.sel_file_but.is_pressed(event):
            # load Image
            file = filedialog.askopenfilename(initialdir="D:\\Golf_course_IMGs")

            if file != "":
                self.Hole_IMG.set_img(file)
                self.Hole_IMG.set_pos(self.WINDOW_SIZE[0] // 2 - self.Hole_IMG.img.width() // 2,
                                      self.WINDOW_SIZE[1] // 2 - self.Hole_IMG.img.height() // 2)

                self.action_text.set_text("select starting pos")
                self.action_text.set_color((0, 0, 0))

        elif self.action_text.txt == "select starting pos":
            self.start_point.set_pos(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

    # scroll event
    def scroll(self, event):
        self.zoom += event.delta/12

        if self.Hole_IMG.src is not None:
            self.Hole_IMG.set_size(self.zoom)
            self.Hole_IMG.set_pos(self.WINDOW_SIZE[0] // 2 - self.Hole_IMG.img.width() // 2,
                                  self.WINDOW_SIZE[1] // 2 - self.Hole_IMG.img.height() // 2)

    # configure event
    def configure(self, event):
        self.WINDOW_SIZE = [event.width, event.height]

        # resize canvas
        self.canvas.configure(width=self.WINDOW_SIZE[0], height=self.WINDOW_SIZE[1])

        # update image
        if self.Hole_IMG.src is not None:
            self.Hole_IMG.set_pos(self.WINDOW_SIZE[0] // 2 - self.Hole_IMG.img.width() // 2,
                                  self.WINDOW_SIZE[1] // 2 - self.Hole_IMG.img.height() // 2)

        # replace canvas objects
        self.sel_file_but.set_pos(self.WINDOW_SIZE[0] // 2 - 210, self.sel_file_but.y)
        self.sel_file_text.set_pos(self.WINDOW_SIZE[0]//2-185, 75-self.F1.measure("linespace")//2)

        self.action_but.set_pos(self.WINDOW_SIZE[0] // 2 + 10, self.sel_file_but.y)
        self.action_text.set_pos(self.WINDOW_SIZE[0]//2+35, 75-self.F1.measure("linespace")//2)

    # open the window
    def main_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
    gui.main_loop()
