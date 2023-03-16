import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
import datetime
import os
from math import sqrt, floor
import csv

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
        self.map.draw()

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

        # label parameters
        self.ratio = None
        self.new_img_width = None
        self.new_img_height = None

        self.label_tool = None
        self.rubber = False
        self.flood_fill = False
        self.fade = False
        self.hide = False
        self.colors = [(25, 250, 100), (25, 200, 50), (25, 200, 25), (25, 150, 25), (25, 100, 25), (240, 240, 25), (25, 50, 25), (100, 100, 255), (255, 255, 255), (110, 110, 110)]

        # working tools
        self.tools_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+187, self.WINDOW_SIZE[1]-75, 150, 50, None, (240, 240, 240), 6)
        self.rubber_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+187, self.WINDOW_SIZE[1]-75, 50, 50, None, (240, 240, 240), 6)
        self.rubber_img = Advanced_Image(self.canvas, self.WINDOW_SIZE[0]//2+212, self.WINDOW_SIZE[1]-50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png", anchor="center")
        self.flood_fill_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+237, self.WINDOW_SIZE[1]-75, 50, 50, None, (240, 240, 240), 6)
        self.flood_fill_img = Advanced_Image(self.canvas, self.WINDOW_SIZE[0]//2+262, self.WINDOW_SIZE[1]-50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png", anchor="center")
        self.fade_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+287, self.WINDOW_SIZE[1]-75, 50, 50, None, (240, 240, 240), 6)
        self.fade_img = Advanced_Image(self.canvas, self.WINDOW_SIZE[0]//2+312, self.WINDOW_SIZE[1]-50, "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png", anchor="center")

        # label fields
        self.label_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-250-87, self.WINDOW_SIZE[1]//2-75, 500, 50, None, (240, 240, 240), 6)
        self.label_green = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-245-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[0], (240, 240, 240), 2)
        self.label_green_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-225-87, self.WINDOW_SIZE[1]//2-50, "green", (0, 0, 0), self.F3, "center")
        self.label_tee = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-195-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[1], (240, 240, 240), 2)
        self.label_tee_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-175-87, self.WINDOW_SIZE[1]//2-50, "tee", (0, 0, 0), self.F3, "center")
        self.label_fairway = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-145-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[2], (240, 240, 240), 2)
        self.label_fairway_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-125-87, self.WINDOW_SIZE[1]//2-50, "fairway", (0, 0, 0), self.F3, "center")
        self.label_srough = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-95-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[3], (240, 240, 240), 2)
        self.label_srough_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-75-87, self.WINDOW_SIZE[1]//2-50, "semi\nrough", (0, 0, 0), self.F3, "center")
        self.label_hrough = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-45-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[4], (240, 240, 240), 2)
        self.label_hrough_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-25-87, self.WINDOW_SIZE[1]//2-50, "high\nrough", (0, 0, 0), self.F3, "center")
        self.label_bunker = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+5-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[5], (240, 240, 240), 2)
        self.label_bunker_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+25-87, self.WINDOW_SIZE[1]//2-50, "bunker", (0, 0, 0), self.F3, "center")
        self.label_forest = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+55-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[6], (240, 240, 240), 2)
        self.label_forest_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+75-87, self.WINDOW_SIZE[1]//2-50, "forest", (0, 0, 0), self.F3, "center")
        self.label_water = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+105-87, self.WINDOW_SIZE[1]//2-70, 40, 40, self.colors[7], (240, 240, 240), 2)
        self.label_water_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+25-87, self.WINDOW_SIZE[1]//2-50, "water", (0, 0, 0), self.F3, "center")
        self.label_out = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0] // 2 + 155-87, self.WINDOW_SIZE[1] // 2 - 70, 40, 40, self.colors[8], (240, 240, 240), 2)
        self.label_out_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0] // 2 + 25-87, self.WINDOW_SIZE[1] // 2 - 50, "out", (0, 0, 0), self.F3, "center")
        self.label_path = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0] // 2 + 205-87, self.WINDOW_SIZE[1] // 2 - 70, 40, 40, self.colors[9], (240, 240, 240), 2)
        self.label_path_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0] // 2 + 25-87, self.WINDOW_SIZE[1] // 2 - 50, "path", (0, 0, 0), self.F3, "center")

        # shift
        self.shift = 0

        # notification objects
        self.notification_back = Advanced_Rectangle(self.canvas, 0, 100, 50, 24, (60, 60, 60), (60, 60, 60), 2)
        self.notification_text = Advanced_Text(self.canvas, 0, 88, "", (200, 200, 200), self.F2, anchor=tk.CENTER)

        # root bind events
        self.root.bind("<Button-1>", self.button_1)
        self.root.bind("<ButtonRelease-1>", self.buttonrelease_1)
        self.root.bind("<Motion>", self.motion)
        self.root.bind("<B1-Motion>", self.b1_motion)
        self.root.bind("<B2-Motion>", self.b2_motion)
        self.root.bind("<MouseWheel>", self.wheel)
        self.root.bind("<Key>", self.key)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<Left>", self.left)
        self.root.bind("<Right>", self.right)
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
        if not self.hide:
            self.map.draw()

        # draw drawing tools
        self.tools_back.draw()
        self.rubber_back.draw()
        self.rubber_img.draw()
        self.flood_fill_back.draw()
        self.flood_fill_img.draw()
        self.fade_back.draw()
        self.fade_img.draw()

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
    def prep_labeling(self):
        # clear start and end point
        self.map.clear_circle("Starting Point")
        self.map.clear_circle("Ending Point")
        
        # center map
        self.map.add_offset(-self.map.x_offset, -self.map.y_offset, None, "b2")
        self.map.add_zoom(1-self.map.zoom)

        # get parameters for new image
        self.ratio = self.distance/sqrt((self.start_point_pos[0]-self.end_point_pos[0])**2+(self.start_point_pos[1]-self.end_point_pos[1])**2)
        self.new_img_width = round(201/self.ratio)
        self.new_img_height = round(600/self.ratio)

        box_size = 3
        for i in range(round(201/box_size)+1):
            self.map.add_line(f"vert: {i}", -self.new_img_width//2+(i*box_size/self.ratio), -self.new_img_height//2, -self.new_img_width//2+(i*box_size/self.ratio), +self.new_img_height//2, 1, (60, 60, 60), True)
        for i in range(round(600/box_size)+1):
            self.map.add_line(f"hor: {i}", -self.new_img_width//2, -self.new_img_height//2+(i*box_size/self.ratio), +self.new_img_width//2, -self.new_img_height//2+(i*box_size/self.ratio), 1, (60, 60, 60), True)

        self.map.add_polygon_map("hole_map", -self.new_img_width//2, -self.new_img_height//2, (box_size/self.ratio), (67, 200), self.colors)

    # undo tool highlighting
    def undo_highlight(self):
        self.label_green.set_color((240, 240, 240), self.label_green.o)
        self.label_tee.set_color((240, 240, 240), self.label_tee.o)
        self.label_fairway.set_color((240, 240, 240), self.label_fairway.o)
        self.label_srough.set_color((240, 240, 240), self.label_srough.o)
        self.label_hrough.set_color((240, 240, 240), self.label_hrough.o)
        self.label_bunker.set_color((240, 240, 240), self.label_bunker.o)
        self.label_forest.set_color((240, 240, 240), self.label_forest.o)
        self.label_water.set_color((240, 240, 240), self.label_water.o)
        self.label_out.set_color((240, 240, 240), self.label_out.o)
        self.label_path.set_color((240, 240, 240), self.label_path.o)

    # shift
    def add_shift(self, dir: str, dis: int = 10):
        self.shift = self.shift+dis if dir == "right" else self.shift-dis
        delta = dis if dir == "right" else -dis

        # add shift to box indicator lines
        for i in range(round(201/3)+1):
            pos = self.map.lines_info[f"vert: {i}"]
            self.map.set_line_pos(f"vert: {i}", pos[0]+delta, pos[1], pos[2]+delta, pos[3])
        for i in range(round(600/3)+1):
            pos = self.map.lines_info[f"hor: {i}"]
            self.map.set_line_pos(f"hor: {i}", pos[0]+delta, pos[1], pos[2]+delta, pos[3])

        # add shift to polygon map
        pos = self.map.polygon_map_info["hole_map"]
        self.map.set_polygon_map_pos("hole_map", pos[0]+delta, pos[1])

    # next button
    def next_button_press(self):
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
            # draw starting point
            self.map.circles["Ending Point"].set_color((200, 200, 200))

            # apply length
            self.distance = int(os.path.basename(self.file_path).split("-")[1])
            self.hole_len_lab.set_text(f"Hole length: {self.distance}")
            self.hole_len_lab.draw()

            # move on to labeling
            self.prep_labeling()
            self.label_status = "shift"
        # moving on to seth shift
        elif self.label_status == "shift":
            self.label_status = "labeling"
            self.save_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\save_icon.png")
        # labeling
        else:
            self.set_notification(
                "You have completed all tasks and are now labeling. if your done with labeling press the save button to save it.")

        self.button_pressed = True

    # save
    def save(self):
        dataset = "C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Data_set\\Dataset.csv"
        with open(dataset, "r") as file:
            reader = csv.reader(file)
            
            starting_point = (self.map.images["Hole"].get_size()[0]/2+self.start_point_pos[0], self.map.images["Hole"].get_size()[1]/2+self.start_point_pos[1])
            ending_point = (self.map.images["Hole"].get_size()[0]/2+self.end_point_pos[0], self.map.images["Hole"].get_size()[1]/2+self.end_point_pos[1])

            saved = False
            rows = []
            for row in reader:
                # overwrite data if datapoint already exists
                if row[0] == os.path.basename(self.file_path)[0:6]:
                    row[1] = self.map.polygon_map["hole_map"].DATA
                    row[2] = self.map.polygon_map["hole_map"].FADE
                    row[3] = starting_point
                    row[4] = ending_point
                    row[5] = self.distance

                    saved = True

                rows.append(row)

            # save changed values
            if saved:
                with open(dataset, 'w', newline='') as file:
                    # Create a writer object and save
                    writer = csv.writer(file)
                    writer.writerows(rows)

            else:
                # create a writer object and save in a new line
                with open(dataset, 'a', newline='') as write_file:
                    writer = csv.writer(write_file)
                    writer.writerow([os.path.basename(self.file_path)[0:6], self.map.polygon_map["hole_map"].DATA, self.map.polygon_map["hole_map"].FADE, starting_point, ending_point, self.distance])

    # left click
    def button_1(self, event):
        self.click_offset = [event.x, event.y]

        self.button_pressed = self.map.button_1(event)

        # select file button
        if self.sel_file_but.is_pressed(event):
            # load Image
            file = filedialog.askopenfilename(initialdir="D:\\Golf_course_IMGs")

            if file != "":
                # reset
                if self.label_status != "Select Image":
                    # erase from screen
                    self.map.clear_all()
                    self.start_point_lab.clear()
                    self.end_point_lab.clear()
                    self.hole_len_lab.clear()

                    # reset text
                    self.start_point_lab.set_text("Starting point:")
                    self.end_point_lab.set_text("Ending point:")
                    self.hole_len_lab.set_text("Hole length:")

                    # reset variables
                    self.start_point_pos = None
                    self.end_point_pos = None

                    # reset save img
                    self.save_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\save_icon_empty.png")

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
                self.set_notification("Label the image before saving it!")
            else:
                self.save()

            self.button_pressed = True

        # next button
        elif self.next_but.is_pressed(event):
            self.next_button_press()

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
            elif self.label_status == "shift":
                self.set_notification("The next step is to move the labeling gird left or right by using the arrow keys to position it for labeling")
            # next step labeling the image
            elif self.label_status == "labeling":
                self.set_notification("The next step is to label the image by clicking on the screen")

            self.button_pressed = True

        # select labeling tool
        elif self.label_back.is_pressed(event):
            # green
            if self.label_green.is_pressed(event):
                self.label_tool = 0
                self.undo_highlight()
                self.label_green.set_color(self.label_green.o)
            # tee
            elif self.label_tee.is_pressed(event):
                self.label_tool = 1
                self.undo_highlight()
                self.label_tee.set_color(self.label_tee.o)
            # fairway
            elif self.label_fairway.is_pressed(event):
                self.label_tool = 2
                self.undo_highlight()
                self.label_fairway.set_color(self.label_fairway.o)
            # semi rough
            elif self.label_srough.is_pressed(event):
                self.label_tool = 3
                self.undo_highlight()
                self.label_srough.set_color(self.label_srough.o)
            # high rough
            elif self.label_hrough.is_pressed(event):
                self.label_tool = 4
                self.undo_highlight()
                self.label_hrough.set_color(self.label_hrough.o)
            # bunker
            elif self.label_bunker.is_pressed(event):
                self.label_tool = 5
                self.undo_highlight()
                self.label_bunker.set_color(self.label_bunker.o)
            # forest
            elif self.label_forest.is_pressed(event):
                self.label_tool = 6
                self.undo_highlight()
                self.label_forest.set_color(self.label_forest.o)
            # water
            elif self.label_water.is_pressed(event):
                self.label_tool = 7
                self.undo_highlight()
                self.label_water.set_color(self.label_water.o)
            # out
            elif self.label_out.is_pressed(event):
                self.label_tool = 8
                self.undo_highlight()
                self.label_out.set_color(self.label_out.o)
            # path of bounds
            elif self.label_path.is_pressed(event):
                self.label_tool = 9
                self.undo_highlight()
                self.label_path.set_color(self.label_path.o)

            self.button_pressed = True

        # rubber
        elif self.rubber_back.is_pressed(event):
            # turn off
            if self.rubber:
                self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png")
                self.rubber = False
            # turn on
            else:
                self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_active.png")
                self.rubber = True

                # deactivate other tools
                if self.flood_fill:
                    self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png")
                    self.flood_fill = False

                if self.fade:
                    self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png")
                    self.fade = False

            self.button_pressed = True

        # flood fill
        elif self.flood_fill_back.is_pressed(event):
            # turn off
            if self.flood_fill:
                self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png")
                self.flood_fill = False
            # turn on
            else:
                self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_active.png")
                self.flood_fill = True

                # deactivate other tools
                if self.rubber:
                    self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png")
                    self.rubber = False

                if self.fade:
                    self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png")
                    self.fade = False

            self.button_pressed = True

        # fade
        elif self.fade_back.is_pressed(event):
            # turn off
            if self.fade:
                self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png")
                self.fade = False
            # turn on
            else:
                self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_active.png")
                self.fade = True

                # deactivate other tools
                if self.rubber:
                    self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png")
                    self.rubber = False

                if self.flood_fill:
                    self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png")
                    self.flood_fill = False

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
            elif self.label_status == "labeling" and not self.button_pressed:
                if self.label_tool is None:
                    self.set_notification("Please select a labeling tool to continue")

                else:
                    x_index = floor((self.map.get_click_pos(event)[0]-self.shift+self.new_img_width//2)*self.ratio/3)
                    y_index = floor((self.map.get_click_pos(event)[1]+self.new_img_height//2)*self.ratio/3)

                    if self.flood_fill:
                        self.map.polygon_map["hole_map"].flood_fill((x_index, y_index), self.label_tool)

                    else:
                        if 0 <= x_index <= 66 and 0 <= y_index <= 199:
                            # change existing one
                            if self.label_tool is not None:
                                self.map.polygon_map["hole_map"].set_index(x_index, y_index, -1 if self.rubber else self.label_tool, self.fade)

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

        # re place drawing tools
        self.tools_back.set_pos(self.WINDOW_SIZE[0]//2+187, self.WINDOW_SIZE[1]-75)
        self.rubber_back.set_pos(self.WINDOW_SIZE[0]//2+187, self.WINDOW_SIZE[1]-75)
        self.rubber_img.set_pos(self.WINDOW_SIZE[0]//2+212, self.WINDOW_SIZE[1]-50)
        self.flood_fill_back.set_pos(self.WINDOW_SIZE[0]//2+237, self.WINDOW_SIZE[1]-75)
        self.flood_fill_img.set_pos(self.WINDOW_SIZE[0]//2+262, self.WINDOW_SIZE[1]-50)
        self.fade_back.set_pos(self.WINDOW_SIZE[0]//2+287, self.WINDOW_SIZE[1]-75)
        self.fade_img.set_pos(self.WINDOW_SIZE[0]//2+312, self.WINDOW_SIZE[1]-50)

        # re place labeling components
        self.label_back.set_pos(self.WINDOW_SIZE[0]//2-250-87, self.WINDOW_SIZE[1]-75)
        self.label_green.set_pos(self.WINDOW_SIZE[0]//2-245-87, self.WINDOW_SIZE[1]-70)
        self.label_tee.set_pos(self.WINDOW_SIZE[0]//2-195-87, self.WINDOW_SIZE[1]-70)
        self.label_fairway.set_pos(self.WINDOW_SIZE[0]//2-145-87, self.WINDOW_SIZE[1]-70)
        self.label_srough.set_pos(self.WINDOW_SIZE[0]//2-95-87, self.WINDOW_SIZE[1]-70)
        self.label_hrough.set_pos(self.WINDOW_SIZE[0]//2-45-87, self.WINDOW_SIZE[1]-70)
        self.label_bunker.set_pos(self.WINDOW_SIZE[0]//2+5-87, self.WINDOW_SIZE[1]-70)
        self.label_forest.set_pos(self.WINDOW_SIZE[0]//2+55-87, self.WINDOW_SIZE[1]-70)
        self.label_water.set_pos(self.WINDOW_SIZE[0]//2+105-87, self.WINDOW_SIZE[1]-70)
        self.label_out.set_pos(self.WINDOW_SIZE[0]//2+155-87, self.WINDOW_SIZE[1]-70)
        self.label_path.set_pos(self.WINDOW_SIZE[0]//2+205-87, self.WINDOW_SIZE[1]-70)
        self.label_green_txt.set_pos(self.WINDOW_SIZE[0]//2-225-87, self.WINDOW_SIZE[1]-50)
        self.label_tee_txt.set_pos(self.WINDOW_SIZE[0]//2-175-87, self.WINDOW_SIZE[1]-50)
        self.label_fairway_txt.set_pos(self.WINDOW_SIZE[0]//2-125-87, self.WINDOW_SIZE[1]-50)
        self.label_srough_txt.set_pos(self.WINDOW_SIZE[0]//2-75-87, self.WINDOW_SIZE[1]-50)
        self.label_hrough_txt.set_pos(self.WINDOW_SIZE[0]//2-25-87, self.WINDOW_SIZE[1]-50)
        self.label_bunker_txt.set_pos(self.WINDOW_SIZE[0]//2+25-87, self.WINDOW_SIZE[1]-50)
        self.label_forest_txt.set_pos(self.WINDOW_SIZE[0]//2+75-87, self.WINDOW_SIZE[1]-50)
        self.label_water_txt.set_pos(self.WINDOW_SIZE[0]//2+125-87, self.WINDOW_SIZE[1]-50)
        self.label_out_txt.set_pos(self.WINDOW_SIZE[0]//2+175-87, self.WINDOW_SIZE[1]-50)
        self.label_path_txt.set_pos(self.WINDOW_SIZE[0]//2+225-87, self.WINDOW_SIZE[1]-50)

        # re place map center
        self.map.set_center(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

        # map origin button and zoom slider
        self.map.set_origin_button_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]-125)
        self.map.set_zoom_slider_pos(self.WINDOW_SIZE[0]//2-100, self.WINDOW_SIZE[1]-113)

    # track mouse movement
    def motion(self, event):
        self.last_x = event.x
        self.last_y = event.y

    # track mouse movement while mousewheel is pressed
    def b2_motion(self, event):
        self.map.add_offset(event.x - self.last_x, event.y - self.last_y, event, "b2")

        self.last_x = event.x
        self.last_y = event.y

    # track mouse movement
    def b1_motion(self, event):
        slider = self.map.add_offset(event.x-self.last_x, event.y-self.last_y, event, "b1")

        if not slider and not self.button_pressed and self.label_status == "labeling":
            # start and end map pos
            start = self.map.get_click_pos(None, pos=(self.last_x, self.last_y))
            end = self.map.get_click_pos(event)
            
            # food fill
            if self.flood_fill:
                x_index = floor((end[0]-self.shift+self.new_img_width//2)*self.ratio/3)
                y_index = floor((end[1]+self.new_img_height//2)*self.ratio/3)

                self.map.polygon_map["hole_map"].flood_fill((x_index, y_index), self.label_tool)

            else:
                # calculate cursor movement variables
                delta_x = start[0]-end[0]
                delta_y = start[1]-end[1]
                steps = round(sqrt(delta_x**2+delta_y**2)/round(3/self.ratio))+1

                for i in range(steps):
                    # calculate intermediate x, y positions
                    x = end[0] + delta_x / steps * i
                    y = end[1] + delta_y / steps * i

                    x_index = floor((x - self.shift + self.new_img_width // 2) * self.ratio / 3)
                    y_index = floor((y + self.new_img_height // 2) * self.ratio / 3)

                    if 0 <= x_index <= 66 and 0 <= y_index <= 199:
                        # change existing one
                        if self.label_tool is not None:
                            self.map.polygon_map["hole_map"].set_index(x_index, y_index, -1 if self.rubber else self.label_tool, self.fade)

        self.last_x = event.x
        self.last_y = event.y

    # track wheel rotation
    def wheel(self, event):
        self.map.add_zoom(-event.delta/1200)

    # key event
    def key(self, event):
        # next button press
        if event.char == "n":
            self.next_button_press()

        # hide
        if event.char == "h":
            self.hide = True

            self.map.polygon_map["hole_map"].clear()

        # rubber
        if event.char == "c":
            # turn off
            if self.rubber:
                self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png")
                self.rubber = False
            # turn on
            else:
                self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_active.png")
                self.rubber = True

                # deactivate other tools
                if self.flood_fill:
                    self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png")
                    self.flood_fill = False
                
                if self.fade:
                    self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png")
                    self.fade = False

        # flood fill
        if event.char == "v":
            # turn off
            if self.flood_fill:
                self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png")
                self.flood_fill = False
            # turn on
            else:
                self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_active.png")
                self.flood_fill = True
                
                # deactivate other tools
                if self.rubber:
                    self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png")
                    self.rubber = False
                    
                if self.fade:
                    self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png")
                    self.fade = False
        
        # fade
        if event.char == "f":
            # turn off
            if self.fade:
                self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_inactive.png")
                self.fade = False
            # turn on
            else:
                self.fade_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\fade_active.png")
                self.fade = True

                # deactivate other tools
                if self.rubber:
                    self.rubber_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\eraser_inactive.png")
                    self.rubber = False

                if self.flood_fill:
                    self.flood_fill_img.set_img("C:\\Users\\nicow\\PycharmProjects\\Golf_hole_GANs\\Icons\\flood_fill_inactive.png")
                    self.flood_fill = False

    # key release
    def key_release(self, event):
        # un hide
        if event.char == "h":
            self.hide = False

            self.map.polygon_map["hole_map"].calc_polygon()
            self.map.polygon_map["hole_map"].draw()

    # left arrow
    def left(self, event):
        if self.label_status == "shift":
            self.add_shift("left", 10)

    # right arrow
    def right(self, event):
        if self.label_status == "shift":
            self.add_shift("right", 10)

    # open the window
    def main_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
    gui.main_loop()
