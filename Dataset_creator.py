import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
import datetime
import os
from math import sqrt, floor, ceil
from PIL import Image

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
        self.F3 = Font(family="Arial", size=8)

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

        # label parameters
        self.ratio = None
        self.new_img_width =  None
        self.new_img_height =  None

        self.label_tool = None
        self.colors = [(25, 250, 100), (25, 200, 50), (25, 200, 25), (25, 150, 25), (25, 100, 25), (240, 240, 25), (25, 50, 25), (100, 100, 255), (255, 255, 255), (110, 110, 110)]

        # label fields
        self.label_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-250, self.WINDOW_SIZE[1]//2-75, 500, 50, None, (240, 240, 240), 6)
        self.label_green = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-245, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[0], 2)
        self.label_green_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-225, self.WINDOW_SIZE[1]//2-50, "green", (0, 0, 0), self.F3, "center")
        self.label_tee = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-195, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[1], 2)
        self.label_tee_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-175, self.WINDOW_SIZE[1]//2-50, "tee", (255, 255, 255), self.F3, "center")
        self.label_fairway = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-145, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[2], 2)
        self.label_fairway_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-125, self.WINDOW_SIZE[1]//2-50, "fairway", (255, 255, 255), self.F3, "center")
        self.label_srough = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-95, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[3], 2)
        self.label_srough_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-75, self.WINDOW_SIZE[1]//2-50, "semi\nrough", (255, 255, 255), self.F3, "center")
        self.label_hrough = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-45, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[4], 2)
        self.label_hrough_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-25, self.WINDOW_SIZE[1]//2-50, "high\nrough", (255, 255, 255), self.F3, "center")
        self.label_bunker = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+5, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[5], 2)
        self.label_bunker_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+25, self.WINDOW_SIZE[1]//2-50, "bunker", (0, 0, 0), self.F3, "center")
        self.label_forest = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+55, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[6], 2)
        self.label_forest_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+75, self.WINDOW_SIZE[1]//2-50, "forest", (255, 255, 255), self.F3, "center")
        self.label_water = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+105, self.WINDOW_SIZE[1]//2-70, 40, 40, None, self.colors[7], 2)
        self.label_water_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+25, self.WINDOW_SIZE[1]//2-50, "water", (255, 255, 255), self.F3, "center")
        self.label_out = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0] // 2 + 155, self.WINDOW_SIZE[1] // 2 - 70, 40, 40, None, self.colors[8], 2)
        self.label_out_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0] // 2 + 25, self.WINDOW_SIZE[1] // 2 - 50, "out", (0, 0, 0), self.F3, "center")
        self.label_path = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0] // 2 + 205, self.WINDOW_SIZE[1] // 2 - 70, 40, 40, None, self.colors[9], 2)
        self.label_path_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0] // 2 + 25, self.WINDOW_SIZE[1] // 2 - 50, "path", (255, 255, 255), self.F3, "center")

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

        # draw labeling components
        self.label_back.draw()
        self.label_green.draw()
        self.label_tee.draw()
        self.label_fairway.draw()
        self.label_srough.draw()
        self.label_hrough.draw()
        self.label_bunker.draw()
        self.label_forest.draw()
        self.label_water.draw()
        self.label_out.draw()
        self.label_path.draw()
        self.label_green_txt.draw()
        self.label_tee_txt.draw()
        self.label_fairway_txt.draw()
        self.label_srough_txt.draw()
        self.label_hrough_txt.draw()
        self.label_bunker_txt.draw()
        self.label_forest_txt.draw()
        self.label_water_txt.draw()
        self.label_out_txt.draw()
        self.label_path_txt.draw()

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

    # prepare everything for labeling
    def prep_labeling(self, event):
        
        self.start_point_pos = [self.start_point_pos[0], self.start_point_pos[1]]
        self.end_point_pos = [self.end_point_pos[0], self.end_point_pos[1]]

        self.map.set_circle_pos("Starting Point", round(self.start_point_pos[0]), round(self.start_point_pos[1]))
        self.map.set_circle_pos("Ending Point", round(self.end_point_pos[0]), round(self.end_point_pos[1]))

        self.start_point_lab.set_text(f"Starting point: {round(self.start_point_pos[0])}, {round(self.start_point_pos[1])}")
        self.end_point_lab.set_text(f"Ending point: {round(self.end_point_pos[0])}, {round(self.end_point_pos[1])}")
        
        # center map
        self.map.add_offset(-self.map.x_offset, -self.map.y_offset, event)
        self.map.add_zoom(1-self.map.zoom)

        # get parameters for new image
        self.ratio = self.distance/sqrt((self.start_point_pos[0]-self.end_point_pos[0])**2+(self.start_point_pos[1]-self.end_point_pos[1])**2)
        self.new_img_width = round(201/self.ratio)
        self.new_img_height = round(600/self.ratio)

        overlay = Image.new("RGBA", (self.new_img_width, self.new_img_height), (0, 0, 0, 0))
        self.map.images["Hole"].add_overlay(overlay)

        box_size = 3
        for i in range(round(201/box_size)+1):
            self.map.add_line(f"vert: {i}", -self.new_img_width//2+(i*box_size/self.ratio), -self.new_img_height//2, -self.new_img_width//2+(i*box_size/self.ratio), +self.new_img_height//2, 1, (60, 60, 60), True)
        for i in range(round(600/box_size)+1):
            self.map.add_line(f"hor: {i}", -self.new_img_width//2, -self.new_img_height//2+(i*box_size/self.ratio), +self.new_img_width//2, -self.new_img_height//2+(i*box_size/self.ratio), 1, (60, 60, 60), True)

    # undo tool highlighting
    def undo_highlight(self):
        self.label_green.set_color(self.label_green.c)
        self.label_tee.set_color(self.label_tee.c)
        self.label_fairway.set_color(self.label_fairway.c)
        self.label_srough.set_color(self.label_srough.c)
        self.label_hrough.set_color(self.label_hrough.c)
        self.label_bunker.set_color(self.label_bunker.c)
        self.label_forest.set_color(self.label_forest.c)
        self.label_water.set_color(self.label_water.c)
        self.label_out.set_color(self.label_out.c)
        self.label_path.set_color(self.label_path.c)

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

                    self.prep_labeling(event)

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
        elif self.len_set_back.is_pressed(event) and self.len_set_back.object is not None:
            self.button_pressed = True

        # select labeling tool
        elif self.label_back.is_pressed(event):
            # green
            if self.label_green.is_pressed(event):
                self.label_tool = 0
                self.undo_highlight()
                self.label_green.set_color(self.label_green.c, outline=(0, 0, 0))
            # tee
            elif self.label_tee.is_pressed(event):
                self.label_tool = 1
                self.undo_highlight()
                self.label_tee.set_color(self.label_tee.c, outline=(0, 0, 0))
            # fairway
            elif self.label_fairway.is_pressed(event):
                self.label_tool = 2
                self.undo_highlight()
                self.label_fairway.set_color(self.label_fairway.c, outline=(0, 0, 0))
            # semi rough
            elif self.label_srough.is_pressed(event):
                self.label_tool = 3
                self.undo_highlight()
                self.label_srough.set_color(self.label_srough.c, outline=(0, 0, 0))
            # high rough
            elif self.label_hrough.is_pressed(event):
                self.label_tool = 4
                self.undo_highlight()
                self.label_hrough.set_color(self.label_hrough.c, outline=(0, 0, 0))
            # bunker
            elif self.label_bunker.is_pressed(event):
                self.label_tool = 5
                self.undo_highlight()
                self.label_bunker.set_color(self.label_bunker.c, outline=(0, 0, 0))
            # forest
            elif self.label_forest.is_pressed(event):
                self.label_tool = 6
                self.undo_highlight()
                self.label_forest.set_color(self.label_forest.c, outline=(255, 255, 255))
            # water
            elif self.label_water.is_pressed(event):
                self.label_tool = 7
                self.undo_highlight()
                self.label_water.set_color(self.label_water.c, outline=(0, 0, 0))
            # out
            elif self.label_out.is_pressed(event):
                self.label_tool = 8
                self.undo_highlight()
                self.label_out.set_color(self.label_out.c, outline=(0, 0, 0))
            # path of bounds
            elif self.label_path.is_pressed(event):
                self.label_tool = 9
                self.undo_highlight()
                self.label_path.set_color(self.label_path.c, outline=(0, 0, 0))

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
            elif self.label_status == "Select Ending-point" and not self.button_pressed:
                if "Ending Point" not in self.map.circles:
                    self.map.add_circle("Ending Point", map_x, map_y, 5, None, (255, 255, 255))
                    self.end_point_lab.set_text(f"Ending point: {round(map_x)}, {round(map_y)}")

                    self.end_point_pos = [round(map_x), round(map_y)]
                else:
                    self.map.set_circle_pos("Ending Point", map_x, map_y)
                    self.end_point_lab.set_text(f"Ending point: {round(map_x)}, {round(map_y)}")

                    self.end_point_pos = [round(map_x), round(map_y)]

            # labeling image
            elif self.label_status == "labeling":
                if self.label_tool is None:
                    self.set_notification("Please select a labeling tool to continue")

                else:
                    x_index = floor((self.map.get_click_pos(event)[0]+self.new_img_width//2)*self.ratio/3)
                    y_index = floor((self.map.get_click_pos(event)[1]+self.new_img_height//2)*self.ratio/3)

                    self.map.images["Hole"].draw_overlay(ceil((x_index*3)/self.ratio), ceil((y_index*3)/self.ratio), floor(3/self.ratio), floor(3/self.ratio), self.colors[self.label_tool])

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

        # re place distance components
        self.len_set_back.set_pos(self.WINDOW_SIZE[0] // 2 - 200, self.WINDOW_SIZE[1] // 2 - 100, False if self.len_set_back.object is None else True)
        self.len_set_tit.set_pos(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2-50)
        self.len_set_entry.set_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]//2-11)
        self.len_set_under.set_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]//2+11, self.WINDOW_SIZE[0]//2+150, self.WINDOW_SIZE[1]//2+11)
        self.len_set_unit.set_pos(self.WINDOW_SIZE[0]//2+150-self.F1.measure("m"), self.WINDOW_SIZE[1]//2+10)
        self.len_set_info_1.set_pos(self.WINDOW_SIZE[0]//2-128, self.WINDOW_SIZE[1]//2+42)
        self.len_set_info_2.set_pos(self.WINDOW_SIZE[0]//2-64, self.WINDOW_SIZE[1]//2+50)
        self.len_set_info_3.set_pos(self.WINDOW_SIZE[0]//2+128, self.WINDOW_SIZE[1]//2+42)

        # re place labeling components
        self.label_back.set_pos(self.WINDOW_SIZE[0]//2-250, self.WINDOW_SIZE[1]-75)
        self.label_green.set_pos(self.WINDOW_SIZE[0]//2-245, self.WINDOW_SIZE[1]-70)
        self.label_tee.set_pos(self.WINDOW_SIZE[0]//2-195, self.WINDOW_SIZE[1]-70)
        self.label_fairway.set_pos(self.WINDOW_SIZE[0]//2-145, self.WINDOW_SIZE[1]-70)
        self.label_srough.set_pos(self.WINDOW_SIZE[0]//2-95, self.WINDOW_SIZE[1]-70)
        self.label_hrough.set_pos(self.WINDOW_SIZE[0]//2-45, self.WINDOW_SIZE[1]-70)
        self.label_bunker.set_pos(self.WINDOW_SIZE[0]//2+5, self.WINDOW_SIZE[1]-70)
        self.label_forest.set_pos(self.WINDOW_SIZE[0]//2+55, self.WINDOW_SIZE[1]-70)
        self.label_water.set_pos(self.WINDOW_SIZE[0]//2+105, self.WINDOW_SIZE[1]-70)
        self.label_out.set_pos(self.WINDOW_SIZE[0]//2+155, self.WINDOW_SIZE[1]-70)
        self.label_path.set_pos(self.WINDOW_SIZE[0]//2+205, self.WINDOW_SIZE[1]-70)
        self.label_green_txt.set_pos(self.WINDOW_SIZE[0]//2-225, self.WINDOW_SIZE[1]-50)
        self.label_tee_txt.set_pos(self.WINDOW_SIZE[0]//2-175, self.WINDOW_SIZE[1]-50)
        self.label_fairway_txt.set_pos(self.WINDOW_SIZE[0]//2-125, self.WINDOW_SIZE[1]-50)
        self.label_srough_txt.set_pos(self.WINDOW_SIZE[0]//2-75, self.WINDOW_SIZE[1]-50)
        self.label_hrough_txt.set_pos(self.WINDOW_SIZE[0]//2-25, self.WINDOW_SIZE[1]-50)
        self.label_bunker_txt.set_pos(self.WINDOW_SIZE[0]//2+25, self.WINDOW_SIZE[1]-50)
        self.label_forest_txt.set_pos(self.WINDOW_SIZE[0]//2+75, self.WINDOW_SIZE[1]-50)
        self.label_water_txt.set_pos(self.WINDOW_SIZE[0]//2+125, self.WINDOW_SIZE[1]-50)
        self.label_out_txt.set_pos(self.WINDOW_SIZE[0]//2+175, self.WINDOW_SIZE[1]-50)
        self.label_path_txt.set_pos(self.WINDOW_SIZE[0]//2+225, self.WINDOW_SIZE[1]-50)

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
