import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
import datetime
import os

from Advanced_Canvas import Advanced_Rectangle, Advanced_Text, Advanced_Image, Advanced_Entry, Advanced_Line
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
        self.F1 = Font(family="Arial", size=12)  # linespace: 18
        self.F2 = Font(family="Arial", size=10)  # linespace: 16

        self.map = Map(self.canvas, self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

        self.map.add_origin_button(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]-125)
        self.map.add_zoom_slider(self.WINDOW_SIZE[0]//2-100, self.WINDOW_SIZE[1]-113)

        self.map.set_to_background(forever=True)

        # other parameters
        self.last_x = 0
        self.last_y = 0
        self.click_offset = None
        self.button_pressed = False

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

        # label information
        self.label_status = "Select Image"

        # date
        self.start_point_pos = None
        self.end_point_pos = None
        self.distance = None

        # info
        self.start_point_lab = Advanced_Text(self.canvas, 10, 10, "Starting point:", (50, 50, 50), self.F2)
        self.end_point_lab = Advanced_Text(self.canvas, 10, 30, "Ending point:", (50, 50, 50), self.F2)
        self.hole_len_lab = Advanced_Text(self.canvas, 10, 50, "Hole length:", (50, 50, 50), self.F2)

        # length definition components
        self.len_set_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-200, self.WINDOW_SIZE[1]//2-100, 400, 200, None, (240, 240, 240), 6)
        self.len_set_tit = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2-50, "type in the length of the hole:", (0, 0, 0), self.F1, "center")
        self.len_set_entry = Advanced_Entry(self.root, self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]//2-11, 290-self.F1.measure("m"), (240, 240, 240), self.F1)
        self.len_set_under = Advanced_Line(self.canvas, self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]//2+11, self.WINDOW_SIZE[0]//2+150, self.WINDOW_SIZE[1]//2+11, 1, (0, 0, 0))
        self.len_set_unit = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+150-self.F1.measure("m"), self.WINDOW_SIZE[1]//2+10, "m", (0, 0, 0), self.F1, "sw")
        self.len_set_info_1 = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-128, self.WINDOW_SIZE[1]//2+42, "click the", (0, 0, 0), self.F2)
        self.len_set_info_2 = Advanced_Image(self.canvas, self.WINDOW_SIZE[0]//2-64, self.WINDOW_SIZE[1]//2+50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\right-arrow.png", "center")
        self.len_set_info_3 = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+128, self.WINDOW_SIZE[1]//2+42, "button or press \"n\" to continue", (0, 0, 0), self.F2, "ne")

        # notification objects
        self.notification_back = Advanced_Rectangle(self.canvas, 0, 100, 50, 24, (60, 60, 60), (60, 60, 60), 2)
        self.notification_text = Advanced_Text(self.canvas, 0, 88, "", (200, 200, 200), self.F2, anchor=tk.CENTER)

        # root bind events
        self.root.bind("<Button-1>", self.button_1)
        self.root.bind("<ButtonRelease-1>", self.buttonrelease_1)
        self.root.bind("<Motion>", self.motion)
        self.root.bind("<B1-Motion>", self.b1_motion)
        self.root.bind("<MouseWheel>", self.wheel)
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
        self.click_offset = [event.x, event.y]

        self.button_pressed = self.map.button_1(event)

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

                self.map.add_img("Hole", 0, 0, self.file_path, anchor="center")

                # move on in the line of events
                self.start_point_lab.draw()

                # set new label status
                self.label_status = "Select Starting-point"

                self.button_pressed = True

        # save button
        elif self.save_but.is_pressed(event):
            if self.label_status != "labeling":
                self.set_notification("The labeling has to be complete to save the file")
            else:
                pass  # save as a file

            self.button_pressed = True

        # next button
        elif self.next_but.is_pressed(event):
            # image has not been selected
            if self.label_status == "Select Image":
                self.set_notification("you have to select an image before moving on")
            # starting point has not been selected
            elif self.label_status == "Select Starting-point" and self.start_point_lab.txt == "Starting point:":
                self.set_notification("Set starting Point before moving on")
            # moving on to ending point selection
            elif self.label_status == "Select Starting-point":
                self.label_status = "Select Ending-point"
                self.map.circles["Starting Point"].set_color((200, 200, 200))
                self.end_point_lab.draw()
            # ending point has not been selected
            elif self.label_status == "Select Ending-point" and self.end_point_lab.txt == "Ending point:":
                self.set_notification("Set ending Point before moving on")
            # moving on to defining length
            elif self.label_status == "Select Ending-point":
                self.label_status = "Select Length"
                self.map.circles["Ending Point"].set_color((200, 200, 200))
                self.hole_len_lab.draw()
                # draw len popup
                self.len_set_back.draw()
                self.len_set_tit.draw()
                self.len_set_entry.draw()
                self.len_set_under.draw()
                self.len_set_unit.draw()
                self.len_set_info_1.draw()
                self.len_set_info_2.draw()
                self.len_set_info_3.draw()
            # moving on to labeling image
            elif self.label_status == "Select Length":
                self.distance = self.len_set_entry.get_text()
                # no input
                if self.distance.strip(" ") == "":
                    self.set_notification("Please set a distance value before moving on")
                # good input
                try:
                    self.distance = int(self.distance.strip(" "))
                    
                    self.hole_len_lab.set_text(f"Hole length: {self.distance}")
                    # clean len popup
                    self.len_set_back.clear()
                    self.len_set_tit.clear()
                    self.len_set_entry.clear()
                    self.len_set_under.clear()
                    self.len_set_unit.clear()
                    self.len_set_info_1.clear()
                    self.len_set_info_2.clear()
                    self.len_set_info_3.clear()

                    self.label_status = "labeling"
                    self.save_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\save_icon.png")
                # input is not an int
                except ValueError:
                    self.set_notification("The input for the length has to be transformable to an int")
            # labeling
            else:
                self.set_notification("You have completed all tasks and are now labeling. if your done with labeling press the save button to save it.")

            self.button_pressed = True

        # information button
        elif self.info_but.is_pressed(event):
            # next step select image
            if self.label_status == "Select Image":
                self.set_notification("The next step is to select an Image by clicking the \"Select Image\" button")
            # next step select starting point
            elif self.label_status == "Select Starting-pint":
                self.set_notification("The next step is to select the start point by clicking on the image")
            # next step select ending point
            elif self.label_status == "Select Ending-point":
                self.set_notification("The next step is to select the ending point by clicking on the image")
            # next step define length
            elif self.label_status == "Select Length":
                self.set_notification("The next step is to define the length by typing it in to the entry in the popup")
            # next step labeling the image
            elif self.label_status == "labeling":
                self.set_notification("The next step is to label the image by clicking on the screen")

            self.button_pressed = True

        # len set label clicked
        if self.len_set_back.is_pressed(event) and self.len_set_back.object is not None:
            self.button_pressed = True

    def buttonrelease_1(self, event):
        self.map.buttonrelease_1(event)

        # check if only click and no movement
        if [event.x, event.y] == self.click_offset:
            map_x, map_y = self.map.get_click_pos(event)

            # add/move starting point
            if self.label_status == "Select Starting-point" and not self.button_pressed:
                if "Starting Point" not in self.map.circles:
                    self.map.add_circle("Starting Point", map_x, map_y, 5, None, (255, 255, 255))
                    self.start_point_lab.set_text(f"Starting point: {round(map_x)}, {round(map_y)}")

                    self.start_point_pos = [round(map_x), round(map_y)]
                else:
                    self.map.set_circle_pos("Starting Point", map_x, map_y)
                    self.start_point_lab.set_text(f"Starting point: {round(map_x)}, {round(map_y)}")

                    self.start_point_pos = [round(map_x), round(map_y)]

            # add/move ending point
            if self.label_status == "Select Ending-point" and not self.button_pressed:
                if "Ending Point" not in self.map.circles:
                    self.map.add_circle("Ending Point", map_x, map_y, 5, None, (255, 255, 255))
                    self.end_point_lab.set_text(f"Ending point: {round(map_x)}, {round(map_y)}")

                    self.end_point_pos = [round(map_x), round(map_y)]
                else:
                    self.map.set_circle_pos("Ending Point", map_x, map_y)
                    self.end_point_lab.set_text(f"Ending point: {round(map_x)}, {round(map_y)}")

                    self.end_point_pos = [round(map_x), round(map_y)]

        self.button_pressed = False

    # configure event
    def configure(self, event):
        self.WINDOW_SIZE = [event.width, event.height]

        # resize canvas
        self.canvas.configure(width=self.WINDOW_SIZE[0], height=self.WINDOW_SIZE[1])

        # re place canvas objects
        self.sel_file_but.set_pos(self.WINDOW_SIZE[0]//2-150, self.sel_file_but.y)
        self.sel_file_text.set_pos(self.WINDOW_SIZE[0]//2-135, 75-self.F1.measure("linespace")//2)

        self.save_but.set_pos(self.WINDOW_SIZE[0]//2-225, self.save_but.y)
        self.save_img.set_pos(self.WINDOW_SIZE[0]//2-200-self.save_img.get_size()[0]//2, 50-self.save_img.get_size()[1]//2)

        self.next_but.set_pos(self.WINDOW_SIZE[0]//2+175, self.next_but.y)
        self.next_img.set_pos(self.WINDOW_SIZE[0]//2+200-self.next_img.get_size()[0]//2, 50-self.next_img.get_size()[1]//2)

        self.info_but.set_pos(self.WINDOW_SIZE[0]-75, self.WINDOW_SIZE[1]-75)
        self.info_img.set_pos(self.WINDOW_SIZE[0]-50-self.next_img.get_size()[0]//2, self.WINDOW_SIZE[1]-50-self.next_img.get_size()[1]//2)

        # re place notification objects
        if self.notification is not None:
            self.notification_back.set_pos(self.WINDOW_SIZE[0]//2-self.F2.measure(self.notification)//2-10, 85)
            self.notification_text.set_pos(self.WINDOW_SIZE[0]//2, 97)

        # re place label components
        self.len_set_back.set_pos(self.WINDOW_SIZE[0] // 2 - 200, self.WINDOW_SIZE[1] // 2 - 100, False if self.len_set_back.object is None else True)
        self.len_set_tit.set_pos(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2-50)
        self.len_set_entry.set_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]//2-11)
        self.len_set_under.set_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]//2+11, self.WINDOW_SIZE[0]//2+150, self.WINDOW_SIZE[1]//2+11)
        self.len_set_unit.set_pos(self.WINDOW_SIZE[0]//2+150-self.F1.measure("m"), self.WINDOW_SIZE[1]//2+10)
        self.len_set_info_1.set_pos(self.WINDOW_SIZE[0]//2-128, self.WINDOW_SIZE[1]//2+42)
        self.len_set_info_2.set_pos(self.WINDOW_SIZE[0]//2-64, self.WINDOW_SIZE[1]//2+50)
        self.len_set_info_3.set_pos(self.WINDOW_SIZE[0]//2+128, self.WINDOW_SIZE[1]//2+42)

        # re place map center
        self.map.set_center(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

        # map origin button and zoom slider
        self.map.set_origin_button_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]-125)
        self.map.set_zoom_slider_pos(self.WINDOW_SIZE[0]//2-100, self.WINDOW_SIZE[1]-113)

    # track mouse movement
    def motion(self, event):
        self.last_x = event.x
        self.last_y = event.y

    # track mouse movement
    def b1_motion(self, event):
        self.map.add_offset(event.x-self.last_x, event.y-self.last_y, event)

        self.last_x = event.x
        self.last_y = event.y

    # track wheel rotation
    def wheel(self, event):
        self.map.add_zoom(-event.delta/1200)

    # open the window
    def main_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
    gui.main_loop()
