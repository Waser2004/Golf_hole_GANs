import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
import datetime
import os

from Advanced_Canvas import Advanced_Rectangle, Advanced_Text, Advanced_Image
from Map import Map


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
        self.F2 = Font(family="Arial", size=10)

        self.map = Map(self.canvas, self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

        # other parameters
        self.last_x = 0
        self.last_y = 0

        self.file_path = None

        self.notification = None
        self.notification_time = None

        # initialise canvas objects
        self.sel_file_but = Advanced_Rectangle(self.canvas, 0, 25, 300, 50, (240, 240, 240), (240, 240, 240), 6)
        self.sel_file_text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-75, 0, "Select Image", (0, 0, 0), self.F1)

        self.save_but = Advanced_Rectangle(self.canvas, 0, 25, 50, 50, (240, 240, 240), (240, 240, 240), 6)
        self.save_img = Advanced_Image(self.canvas, 0, 50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\save_icon_empty.png")

        self.next_but = Advanced_Rectangle(self.canvas, 0, 25, 50, 50, (240, 240, 240), (240, 240, 240), 6)
        self.next_img = Advanced_Image(self.canvas, 0, 50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\right-arrow.png")

        self.info_but = Advanced_Rectangle(self.canvas, 0, 25, 50, 50, (240, 240, 240), (240, 240, 240), 6)
        self.info_img = Advanced_Image(self.canvas, 0, 50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\info-button.png")

        # notification objects
        self.notification_back = Advanced_Rectangle(self.canvas, 0, 100, 50, 24, (60, 60, 60), (60, 60, 60), 2)
        self.notification_text = Advanced_Text(self.canvas, 0, 88, "", (200, 200, 200), self.F2, anchor=tk.CENTER)

        # root bind events
        self.root.bind("<Button-1>", self.button_1)
        self.root.bind("<Motion>", self.motion)
        self.root.bind("<B1-Motion>", self.b1_motion)
        self.root.bind_class("Tk", "<Configure>", self.configure)

    # window loop
    def main(self):
        # draw canvas objects
        self.sel_file_but.draw()
        self.sel_file_text.draw()

        self.save_but.draw()
        self.save_img.draw()

        self.next_but.draw()
        self.next_img.draw()

        self.info_but.draw()
        self.info_img.draw()

        # clear notification
        if self.notification_time is not None and (datetime.datetime.now()-self.notification_time).seconds >= 5:
            # clear parameters
            self.notification_back.clear()
            self.notification_text.clear()
            # reset
            self.notification = None
            self.notification_time = None

        # draw map
        self.map.draw()

        self.root.after(27, self.main)

    # set a notification
    def set_notification(self, txt: str):
        # assign notification text
        self.notification = txt

        # update notification vis parameters
        self.notification_back.set_pos(self.WINDOW_SIZE[0]//2-self.F2.measure(self.notification)//2-10, 85)
        self.notification_back.set_size(self.F2.measure(self.notification)+20, 24)

        self.notification_text.set_text(self.notification)
        self.notification_text.set_pos(self.WINDOW_SIZE[0]//2, 97)

        # draw notification text
        self.notification_text.draw()

        # start notification timer
        self.notification_time = datetime.datetime.now()

    # left click
    def button_1(self, event):
        # select file button
        if self.sel_file_but.is_pressed(event):
            # load Image
            file = filedialog.askopenfilename(initialdir="D:\\Golf_course_IMGs")

            if file != "":
                # assign file path
                self.file_path = file

                # get file name and shorten it if needed
                txt = os.path.basename(self.file_path)
                while self.F1.measure(f"{txt}...") > 270:
                    txt = txt[:-2]
                txt += "..." if self.F1.measure(f"{os.path.basename(self.file_path)}...") > 270 else ""

                # update text object
                self.sel_file_text.set_text(txt)

        # save button
        elif self.save_but.is_pressed(event):
            if self.file_path is None:
                self.set_notification("you have to select a file before you can save anything")
            else:
                self.set_notification("The labeling has to be complete to save the file")

        # next button
        elif self.next_but.is_pressed(event):
            if self.file_path is None:
                self.set_notification("you have to select a file before moving on")
            else:
                self.set_notification("Set starting Point before moving on")

        # information button
        elif self.info_but.is_pressed(event):
            if self.file_path is None:
                self.set_notification("The next step is to select an Image by clicking the \"Select Image\" button")
            else:
                self.set_notification("The next step is to select the start point by clicking on the image")

    # configure event
    def configure(self, event):
        self.WINDOW_SIZE = [event.width, event.height]

        # resize canvas
        self.canvas.configure(width=self.WINDOW_SIZE[0], height=self.WINDOW_SIZE[1])

        # replace canvas objects
        self.sel_file_but.set_pos(self.WINDOW_SIZE[0]//2-150, self.sel_file_but.y)
        self.sel_file_text.set_pos(self.WINDOW_SIZE[0]//2-135, 75-self.F1.measure("linespace")//2)

        self.save_but.set_pos(self.WINDOW_SIZE[0]//2-225, self.save_but.y)
        self.save_img.set_pos(self.WINDOW_SIZE[0]//2-200-self.save_img.get_size()[0]//2, 50-self.save_img.get_size()[1]//2)

        self.next_but.set_pos(self.WINDOW_SIZE[0]//2+175, self.next_but.y)
        self.next_img.set_pos(self.WINDOW_SIZE[0]//2+200-self.next_img.get_size()[0]//2, 50-self.next_img.get_size()[1]//2)

        self.info_but.set_pos(self.WINDOW_SIZE[0]-75, self.WINDOW_SIZE[1]-75)
        self.info_img.set_pos(self.WINDOW_SIZE[0]-50-self.next_img.get_size()[0]//2, self.WINDOW_SIZE[1]-50-self.next_img.get_size()[1]//2)

        # replace notification objects
        if self.notification is not None:
            self.notification_back.set_pos(self.WINDOW_SIZE[0]//2-self.F2.measure(self.notification)//2-10, 85)
            self.notification_text.set_pos(self.WINDOW_SIZE[0]//2, 97)

        # replace map center
        self.map.set_center(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

    # track mouse movement
    def motion(self, event):
        self.last_x = event.x
        self.last_y = event.y

    # track mouse movement
    def b1_motion(self, event):
        self.map.add_offset(event.x-self.last_x, event.y-self.last_y)

        self.last_x = event.x
        self.last_y = event.y

    # open the window
    def main_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
    gui.main_loop()
