import copy
import tkinter as tk
from tkinter.font import Font
from tkinter import filedialog
import datetime
import os
from math import sqrt, floor
import csv
import ast

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
        self.save_img = Advanced_Image(self.canvas, 0, 50, "Icons\\save_icon_empty.png")

        self.next_but = Advanced_Rectangle(self.canvas, 0, 25, 50, 50, (240, 240, 240), (240, 240, 240), 6)
        self.next_img = Advanced_Image(self.canvas, 0, 50, "Icons\\right-arrow_inactive.png")

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
        self.label_tool = None

        self.colors = [(50, 205, 50), (104, 155, 64), (33, 153, 50), (154, 205, 50), (128, 128, 0), (210, 180, 140), (240, 230, 140), (85, 107, 47), (70, 130, 180), (255, 255, 255), (128, 128, 128), (226, 114, 91)]
        self.color_texts = ["green", "tee", "fairway", "semi\nrough", "high\nrough", "bunker", "waste\narea", "forest", "water", "out", "path", "house"]

        self.color_labels = []

        # label fields
        self.label_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-(len(self.colors)*50)//2, self.WINDOW_SIZE[1]//2-75, len(self.colors)*50, 50, None, (240, 240, 240), 6)
        for i, txt in enumerate(zip(self.color_texts, self.colors)):
            back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-(i*50)//2-5, self.WINDOW_SIZE[1]//2-70, 40, 40, txt[1], (240, 240, 240), 2)
            text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-(i*50)//2+15, self.WINDOW_SIZE[1]//2-50, txt[0], (0, 0, 0), self.F3, "center")
            self.color_labels.append([back, text])

        # undo and redo parameters
        self.actions_list = []
        self.actions_index = -1

        # undo and redo buttons
        self.undo_but_back = Advanced_Rectangle(self.canvas, 0, 25, 25, 25, None, (240, 240, 240), 6)
        self.undo_but_img = Advanced_Image(self.canvas, 0, 30, "Icons\\undo_icon_inactive.png", "nw")
        self.redo_but_back = Advanced_Rectangle(self.canvas, 0, 25, 25, 25, None, (240, 240, 240), 6)
        self.redo_but_img = Advanced_Image(self.canvas, 0, 30, "Icons\\redo_icon_inactive.png", "nw")

        # popup indicator
        self.dis_cha = False
        # discard changes popup
        self.dis_cha_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-152, self.WINDOW_SIZE[1]//2-74, 304, 148, None, (240, 240, 240), 6)
        self.dis_cha_img = Advanced_Image(self.canvas, self.WINDOW_SIZE[0]//2-115, self.WINDOW_SIZE[1]//2-17, "Icons/trashcan.png", anchor="center")
        self.dis_cha_text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-93, self.WINDOW_SIZE[1]//2-17, "You have made changes.\ndo you want to discard or save them?", (0, 0, 0), font=self.F2, anchor="w")
        self.dis_cha_cancel_but = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-142, self.WINDOW_SIZE[1]//2+39, 88, 25, None, (155, 165, 166), 2)
        self.dis_cha_cancel_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-98, self.WINDOW_SIZE[1]//2+51, "cancel", (240, 240, 240), font=self.F3, anchor="c")
        self.dis_cha_remove_but = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-44, self.WINDOW_SIZE[1]//2+39, 88, 25, None, (231, 76, 60), 2)
        self.dis_cha_remove_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2+51, "discard changes", (240, 240, 240), font=self.F3, anchor="c")
        self.dis_cha_save_but = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+54, self.WINDOW_SIZE[1]//2+39, 88, 25, None, (46, 113, 204), 2)
        self.dis_cha_save_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+98, self.WINDOW_SIZE[1]//2+51, "save changes", (240, 240, 240), font=self.F3, anchor="c")

        # popup indicator
        self.load_data = False
        # load data popup
        self.load_data_back = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-103, self.WINDOW_SIZE[1]//2-58, 206, 116, None, (240, 240, 240), 6)
        self.load_data_text = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2-17, "Data available!\nload or create new data", (0, 0, 0), font=self.F2, anchor="c")
        self.load_data_new_but = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2-93, self.WINDOW_SIZE[1]//2+23, 88, 25, None, (155, 165, 166), 2)
        self.load_data_new_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2-49, self.WINDOW_SIZE[1]//2+36, "create new", (240, 240, 240), font=self.F3, anchor="c")
        self.load_data_load_but = Advanced_Rectangle(self.canvas, self.WINDOW_SIZE[0]//2+5, self.WINDOW_SIZE[1]//2+23, 88, 25, None, (46, 113, 204), 2)
        self.load_data_load_txt = Advanced_Text(self.canvas, self.WINDOW_SIZE[0]//2+49, self.WINDOW_SIZE[1]//2+36, "load data", (240, 240, 240), font=self.F3, anchor="c")

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
        self.root.bind("<Return>", self.enter)
        self.root.bind("<Escape>", self.enter)
        self.root.bind("<BackSpace>", self.backspace)
        self.root.bind("<Delete>", self.backspace)
        self.root.bind("<Key>", self.key)
        self.root.bind("<KeyPress-c>", self.keypress)
        self.root.bind("<KeyRelease-c>", self.keyrelease)
        self.root.bind("<Up>", self.up)
        self.root.bind("<Down>", self.down)
        self.root.bind("<Control-z>", self.control_z)
        self.root.bind("<Control-s>", self.save)
        self.root.bind("<Control-Shift-Z>", self.control_shift_z)
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

        # clear notification
        if self.notification_time is not None and (datetime.datetime.now()-self.notification_time).seconds >= 5:
            # clear parameters
            self.notification_back.clear()
            self.notification_text.clear()
            # reset
            self.notification = None
            self.notification_time = None

        # draw discard changes popup
        if self.dis_cha:
            self.dis_cha_back.draw()
            self.dis_cha_img.draw()
            self.dis_cha_text.draw()
            self.dis_cha_save_but.draw()
            self.dis_cha_save_txt.draw()
            self.dis_cha_cancel_but.draw()
            self.dis_cha_cancel_txt.draw()
            self.dis_cha_remove_but.draw()
            self.dis_cha_remove_txt.draw()

        # draw load data popup
        if self.load_data:
            self.load_data_back.draw()
            self.load_data_text.draw()
            self.load_data_new_but.draw()
            self.load_data_new_txt.draw()
            self.load_data_load_but.draw()
            self.load_data_load_txt.draw()

        # draw labeling components
        self.label_back.draw()
        for value in self.color_labels:
            value[0].draw()
            value[1].draw()

        # draw map
        self.map.draw()

        # draw undo/redo buttons
        self.undo_but_back.draw()
        self.undo_but_img.draw()
        self.redo_but_back.draw()
        self.redo_but_img.draw()

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
        self.map.add_bezier_map("Hole_map", 0, 0, self.colors)

    # undo tool highlighting
    def undo_highlight(self):
        for i, value in enumerate(self.color_labels):
            value[0].set_color((240, 240, 240), value[0].o)

    # next button
    def next_button_press(self, shortcut: bool = False):
        # button active
        if self.next_img.src == "Icons/right-arrow.png":
            # moving on to ending point selection
            if self.label_status == "Select Starting-point":
                self.label_status = "Select Ending-point"
                self.map.circles["Starting Point"].set_color((200, 200, 200))
                self.end_point_lab.draw()

            # moving on to labeling
            elif self.label_status == "Select Ending-point":
                # apply length
                self.distance = int(os.path.basename(self.file_path).split("-")[1])
                self.hole_len_lab.set_text(f"Hole length: {self.distance}")
                self.hole_len_lab.draw()

                # move on to labeling
                self.prep_labeling()
                self.label_status = "labeling"

            # turn next button to inactive
            self.next_img.set_img("Icons/right-arrow_inactive.png")
        # button inactive
        else:
            # image has not been selected
            if self.label_status == "Select Image":
                self.set_notification("Select image to continue")

            # starting point has not been selected
            elif self.label_status == "Select Starting-point" and self.start_point_lab.txt == "Starting point:":
                self.set_notification("Set starting point to continue")

            # ending point has not been selected
            elif self.label_status == "Select Ending-point" and self.end_point_lab.txt == "Ending point:":
                self.set_notification("Set ending Point to continue")
            # labeling
            else:
                self.set_notification("No need to press next button. Label the image and press the save button to save the data")

        # there was a button press
        if not shortcut:
            self.button_pressed = True

    # save
    def save(self, event = None):
        if self.map.bezier_map_exists("Hole_map"):
            self.map.bezier_map["Hole_map"].prep_for_save()
            data = self.map.bezier_map["Hole_map"]

            # clear history
            data.history.clear()
            data.history_index = -1
            self.undo_but_img.set_img("Icons/undo_icon_inactive.png")
            self.redo_but_img.set_img("Icons/redo_icon_inactive.png")
            self.save_img.set_img("Icons/save_icon_empty.png")

            dis = sqrt((self.start_point_pos[0]-self.end_point_pos[0])**2+(self.start_point_pos[1]-self.end_point_pos[1])**2)
            ratio = self.distance/dis

            # poly points
            norm_points_poly = copy.deepcopy(data.points_poly_map)

            # add point type to polygon points
            for poly_index, polygon in enumerate(norm_points_poly):
                for point_index, p in enumerate(polygon):
                    if type(data.can_bezier_points[poly_index][point_index]) == Advanced_Rectangle:
                        norm_points_poly[poly_index][point_index] = [p, True]
                    else:
                        norm_points_poly[poly_index][point_index] = [p, False]

            norm_points_poly = copy.deepcopy([norm_points_poly[i] for i in reversed(data.z_order)])

            # tee and green pos
            start_pos = copy.copy(self.start_point_pos)
            end_pos = copy.copy(self.end_point_pos)

            # update colors, fade
            norm_colors = copy.deepcopy([data.colors.index(data.poly_colors[i]) for i in reversed(data.z_order)])
            norm_fade = copy.deepcopy([[[f_i[0], f_i[1], f_i[3]] for f_i in data.can_fade[z_i]] for z_i in reversed(data.z_order)])

            # open the csv file and read all the rows
            with open("Data_set/Dataset.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                rows = [row for row in csv_reader]

            # search if image has been saved already
            for i, row in enumerate(rows):
                if len(row) > 0:
                    if os.path.basename(self.file_path)[0:6] == row[0]:
                        # modify rows
                        rows[i] = [os.path.basename(self.file_path)[0:6], ratio, start_pos, end_pos, norm_points_poly, norm_fade, norm_colors]
                        # write rows to csv file
                        with open("Data_set/Dataset.csv", 'w', newline='') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerows(rows)
                        break
            else:
                # save new row
                with open("Data_set/Dataset.csv", "a") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([os.path.basename(self.file_path)[0:6], ratio, start_pos, end_pos, norm_points_poly, norm_fade, norm_colors])

            # open the csv file and read all the rows
            with open("Data_set/Dataset.csv", "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                rows = [row for row in csv_reader if row]
            # write rows to csv file
            with open("Data_set/Dataset.csv", 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerows(rows)

    # select image but is pressed
    def select_image_but_press(self):
        # search for already saved data
        with open("Data_set/Dataset.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = [row[0] for row in csv_reader if len(row) > 0]

        # search for already saved files
        file_list = [filename for filename in os.listdir("D:\\Ondrive\\OneDrive - Venusnet\\Golf_course_IMGs") if
                     rows.count(filename[0:6])]

        # define file types
        if len(file_list) > 0:
            filetypes = (
                ("load image", "*.png"),
                ("load data", file_list),
                ("all files", "*.*")
            )
        # no data to load
        else:
            filetypes = (
                ("load image", "*.png"),
                ("all files", "*.*")
            )

        # load Image
        file = filedialog.askopenfilename(initialdir="D:\\Ondrive\\OneDrive - Venusnet\\Golf_course_IMGs", filetypes=filetypes)
        # assign file path
        if file != "":
            self.file_path = file

            # there is data open popup
            if file_list.count(os.path.basename(self.file_path)):
                self.load_data = True
                self.set_load_data_pos()

            # there is no data available
            else:
                self.load_image()

    # load data
    def load_from_csv(self):
        # load image
        self.load_image()

        # open the csv file and read all the rows
        with open("Data_set/Dataset.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            rows = [row for row in csv_reader if row and row[0] == os.path.basename(self.file_path)[0:6]]

        data = [rows[0][0], float(rows[0][1]), ast.literal_eval(rows[0][2]), ast.literal_eval(rows[0][3]), ast.literal_eval(rows[0][4]), ast.literal_eval(rows[0][5]), ast.literal_eval(rows[0][6])]

        # starting point
        self.start_point_lab.set_text(f"Starting point: {round(data[2][0])}, {round(data[2][1])}")
        self.start_point_pos = [round(data[2][0]), round(data[2][1])]
        self.start_point_lab.draw()

        # end point
        self.end_point_lab.set_text(f"Ending point: {round(data[3][0])}, {round(data[3][1])}")
        self.end_point_pos = [round(data[3][0]), round(data[3][1])]
        self.end_point_lab.draw()

        # distance
        self.distance = int(os.path.basename(self.file_path).split("-")[1])
        self.hole_len_lab.set_text(f"Hole length: {self.distance}")
        self.hole_len_lab.draw()

        # create bezier map
        self.map.add_bezier_map("Hole_map", 0, 0, self.colors)
        self.map.bezier_map["Hole_map"].load_data(data[4], data[5], data[6])

        # set mode to labeling mode
        self.label_status = "labeling"

    # load image
    def load_image(self):
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
            self.save_img.set_img("Icons\\save_icon_empty.png")

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

        # turn next button to inactive
        self.next_img.set_img("Icons/right-arrow_inactive.png")

    # left click
    def button_1(self, event):
        if not self.dis_cha and not self.load_data:
            self.click_offset = [event.x, event.y]

            self.button_pressed = self.map.button_1(event)

            # select file button
            if self.sel_file_but.is_pressed(event):
                # only load image if None was selected before
                if self.file_path is None:
                    self.select_image_but_press()
                # changes have been made that weren't saved
                elif self.map.bezier_map_exists("Hole_map") and len(self.map.bezier_map["Hole_map"].history) > 0:
                    self.dis_cha = True
                    self.set_dis_cha_pos()
                # everything has been saved
                else:
                    if self.map.bezier_map_exists("Hole_map"):
                        self.map.bezier_map["Hole_map"].clear()
                    self.select_image_but_press()

                self.button_pressed = True

            # save button
            elif self.save_but.is_pressed(event):
                if self.label_status != "labeling":
                    self.set_notification("Label the image before saving it!")
                else:
                    if self.save_img.src == "Icons/save_icon.png":
                        self.set_notification(f"data from {os.path.basename(self.file_path)} has been saved")
                        self.save()
                    else:
                        self.set_notification("all data has already been saved")

                self.button_pressed = True

            # next button
            elif self.next_but.is_pressed(event):
                self.next_button_press()

            # undo button is pressed
            elif self.undo_but_back.is_pressed(event):
                if self.map.bezier_map["Hole_map"].history_index == -1:
                    self.set_notification("nothing to undo")

                self.map.bezier_map["Hole_map"].undo()

                # update images
                if self.map.bezier_map["Hole_map"].history_index == -1:
                    self.undo_but_img.set_img("Icons\\undo_icon_inactive.png")
                    self.save_img.set_img("Icons/save_icon_empty.png")
                if self.redo_but_img.src == "Icons\\redo_icon_inactive.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_active.png")

                self.button_pressed = True

            # redo button is pressed
            elif self.redo_but_back.is_pressed(event):
                if self.map.bezier_map["Hole_map"].history_index == len(self.map.bezier_map["Hole_map"].history) - 1:
                    self.set_notification("nothing to redo")

                self.map.bezier_map["Hole_map"].redo()

                # update images
                if self.map.bezier_map["Hole_map"].history_index == len(self.map.bezier_map["Hole_map"].history) - 1:
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")
                    self.save_img.set_img("Icons/save_icon.png")

                self.button_pressed = True

            # select labeling tool
            elif self.label_back.is_pressed(event):
                # select label color
                if self.label_status == "labeling":
                    for i, value in enumerate(self.color_labels):
                        if value[0].is_pressed(event):
                            self.label_tool = i
                            self.undo_highlight()
                            value[0].set_color(value[0].o)

                            self.button_pressed = True
                            break
                # complete other tasks before labeling the image
                else:
                    self.set_notification("Select image, starting and ending point before labeling the image")

            # map is pressed
            elif not self.button_pressed and self.map.bezier_map_exists("Hole_map"):
                history = self.map.bezier_map["Hole_map"].button_1(event, self.label_tool)
                if history and self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if history and self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                # update undo image
                if len(self.map.bezier_map["Hole_map"].history) > 0 and self.undo_but_img.src != "Icons/undo_icon_active.png":
                    self.undo_but_img.set_img("Icons/undo_icon_active.png")
                    self.save_img.set_img("Icons/save_icon.png")

                # reset label tool
                if (self.map.bezier_map["Hole_map"].poly_index is not None and len(self.map.bezier_map["Hole_map"].can_bezier_points[self.map.bezier_map["Hole_map"].poly_index]) == 1) or self.map.bezier_map["Hole_map"].circle_creation:
                    self.label_tool = None
                    self.undo_highlight()

        elif self.dis_cha:
            # cancel button is pressed
            if self.dis_cha_cancel_but.is_pressed(event):
                self.dis_cha = False
                self.clear_dis_cha()
            # discard changes button is pressed
            elif self.dis_cha_remove_but.is_pressed(event):
                self.dis_cha = False
                self.clear_dis_cha()
                if self.map.bezier_map_exists("Hole_map"):
                    self.map.bezier_map["Hole_map"].clear()
                self.select_image_but_press()
            # save button is pressed
            elif self.dis_cha_save_but.is_pressed(event):
                self.dis_cha = False
                self.clear_dis_cha()
                self.save()
                if self.map.bezier_map_exists("Hole_map"):
                    self.map.bezier_map["Hole_map"].clear()
                self.select_image_but_press()

        elif self.load_data:
            # new data is pressed
            if self.load_data_new_but.is_pressed(event):
                self.load_data = False
                self.clear_load_data()
                self.load_image()
            # load data is pressed
            if self.load_data_load_but.is_pressed(event):
                self.load_data = False
                self.clear_load_data()
                self.load_from_csv()

    def buttonrelease_1(self, event):
        if not self.dis_cha and not self.load_data:
            self.map.buttonrelease_1(event)

            # point movement to history
            if self.map.bezier_map_exists("Hole_map"):
                self.map.bezier_map["Hole_map"].add_point_movement_history()

            map_x, map_y = self.map.get_click_pos(event)
            # add/move starting point
            if self.label_status == "Select Starting-point" and not self.button_pressed:
                if "Starting Point" not in self.map.circles:
                    self.map.add_circle("Starting Point", map_x, map_y, 5, None, (255, 255, 255))
                    self.start_point_lab.set_text(f"Starting point: {round(map_x)}, {round(map_y)}")

                    self.start_point_pos = [round(map_x), round(map_y)]

                    # turn next button to active
                    self.next_img.set_img("Icons/right-arrow.png")
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

                    # turn next button to active
                    self.next_img.set_img("Icons/right-arrow.png")
                else:
                    self.map.set_circle_pos("Ending Point", map_x, map_y)
                    self.end_point_lab.set_text(f"Ending point: {round(map_x)}, {round(map_y)}")

                    self.end_point_pos = [round(map_x), round(map_y)]

            # end circle creation
            elif self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].circle_creation:
                # add to history
                self.map.bezier_map["Hole_map"].add_history("cir_creation", self.map.bezier_map["Hole_map"].get_circle_information())
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                self.map.bezier_map["Hole_map"].finish_circle_creation()

            self.button_pressed = False
        
    # set discard changes pop_up pos
    def set_dis_cha_pos(self):
        self.dis_cha_back.set_pos(self.WINDOW_SIZE[0]//2-152, self.WINDOW_SIZE[1]//2-74)
        self.dis_cha_img.set_pos(self.WINDOW_SIZE[0]//2-115, self.WINDOW_SIZE[1]//2-17)
        self.dis_cha_text.set_pos(self.WINDOW_SIZE[0]//2-93, self.WINDOW_SIZE[1]//2-17)
        self.dis_cha_cancel_but.set_pos(self.WINDOW_SIZE[0]//2-142, self.WINDOW_SIZE[1]//2+39)
        self.dis_cha_cancel_txt.set_pos(self.WINDOW_SIZE[0]//2-98, self.WINDOW_SIZE[1]//2+51)
        self.dis_cha_remove_but.set_pos(self.WINDOW_SIZE[0]//2-44, self.WINDOW_SIZE[1]//2+39)
        self.dis_cha_remove_txt.set_pos(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2+51)
        self.dis_cha_save_but.set_pos(self.WINDOW_SIZE[0]//2+54, self.WINDOW_SIZE[1]//2+39)
        self.dis_cha_save_txt.set_pos(self.WINDOW_SIZE[0]//2+98, self.WINDOW_SIZE[1]//2+51)

    # set load data pop_up position
    def set_load_data_pos(self):
        self.load_data_back.set_pos(self.WINDOW_SIZE[0]//2-103, self.WINDOW_SIZE[1]//2-58)
        self.load_data_text.set_pos(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2-17)
        self.load_data_new_but.set_pos(self.WINDOW_SIZE[0]//2-93, self.WINDOW_SIZE[1]//2+23)
        self.load_data_new_txt.set_pos(self.WINDOW_SIZE[0]//2-49, self.WINDOW_SIZE[1]//2+36)
        self.load_data_load_but.set_pos(self.WINDOW_SIZE[0]//2+5, self.WINDOW_SIZE[1]//2+23)
        self.load_data_load_txt.set_pos(self.WINDOW_SIZE[0]//2+49, self.WINDOW_SIZE[1]//2+36)

    # clear discard changes pop_up
    def clear_dis_cha(self):
        self.dis_cha_back.clear()
        self.dis_cha_img.clear()
        self.dis_cha_text.clear()
        self.dis_cha_cancel_but.clear()
        self.dis_cha_cancel_txt.clear()
        self.dis_cha_remove_but.clear()
        self.dis_cha_remove_txt.clear()
        self.dis_cha_save_but.clear()
        self.dis_cha_save_txt.clear()

    # clear load data pop_up
    def clear_load_data(self):
        self.load_data_back.clear()
        self.load_data_text.clear()
        self.load_data_new_but.clear()
        self.load_data_new_txt.clear()
        self.load_data_load_but.clear()
        self.load_data_load_txt.clear()

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

        # re place notification objects
        if self.notification is not None:
            self.notification_back.set_pos(self.WINDOW_SIZE[0]//2-self.F2.measure(self.notification)//2-10, 85)
            self.notification_text.set_pos(self.WINDOW_SIZE[0]//2, 97)

        # re place undo/redo buttons
        self.undo_but_back.set_pos(self.WINDOW_SIZE[0]//2-275, 25)
        self.undo_but_img.set_pos(self.WINDOW_SIZE[0]//2-270, 30)
        self.redo_but_back.set_pos(self.WINDOW_SIZE[0]//2+250, 25)
        self.redo_but_img.set_pos(self.WINDOW_SIZE[0]//2+255, 30)

        # update pop_up_pos
        if self.dis_cha:
            self.set_dis_cha_pos()

        # update pop_up_pos
        if self.load_data:
            self.set_load_data_pos()

        # re place labeling components
        self.label_back.set_pos(self.WINDOW_SIZE[0]//2-(len(self.colors)*50)//2, self.WINDOW_SIZE[1]-75)
        for i, value in enumerate(self.color_labels):
            value[0].set_pos(self.WINDOW_SIZE[0]//2-(len(self.colors)*50)//2+(i*50)+5, self.WINDOW_SIZE[1]-70)
            value[1].set_pos(self.WINDOW_SIZE[0]//2-(len(self.colors)*50)//2+(i*50)+25, self.WINDOW_SIZE[1]-50)

        # re place map center
        self.map.set_center(self.WINDOW_SIZE[0]//2, self.WINDOW_SIZE[1]//2)

        # map origin button and zoom slider
        self.map.set_origin_button_pos(self.WINDOW_SIZE[0]//2-150, self.WINDOW_SIZE[1]-125)
        self.map.set_zoom_slider_pos(self.WINDOW_SIZE[0]//2-100, self.WINDOW_SIZE[1]-113)

    # track mouse movement
    def motion(self, event):
        if not self.dis_cha and not self.load_data:
            self.last_x = event.x
            self.last_y = event.y

            if self.map.bezier_map_exists("Hole_map"):
                self.map.bezier_map["Hole_map"].motion(event)

    # track mouse movement while mousewheel is pressed
    def b2_motion(self, event):
        if not self.dis_cha and not self.load_data:
            self.map.add_offset(event.x-self.last_x, event.y-self.last_y, event, "b2")

            self.last_x = event.x
            self.last_y = event.y

    # track mouse movement
    def b1_motion(self, event):
        if not self.dis_cha and not self.load_data:
            # set map offset
            self.map.add_offset(event.x-self.last_x, event.y-self.last_y, event, "b1")

            if self.map.bezier_map_exists("Hole_map"):
                self.map.bezier_map["Hole_map"].scale_circle(event)

            self.last_x = event.x
            self.last_y = event.y

    # track wheel rotation
    def wheel(self, event):
        if not self.dis_cha and not self.load_data:
            self.map.add_zoom(-event.delta/1200)

    # enter event
    def enter(self, event):
        if not self.dis_cha and not self.load_data:
            if self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].poly_index is not None:
                # calculate new outline
                if self.map.bezier_map["Hole_map"].edit:
                    self.map.bezier_map["Hole_map"].edit_unselected()
                    # add to history
                    self.map.bezier_map["Hole_map"].add_history("unedi_poly", [self.map.bezier_map["Hole_map"].sel_point])
                    if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                        self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                    if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                        self.undo_but_img.set_img("Icons\\undo_icon_active.png")
                # unselect fade
                elif self.map.bezier_map["Hole_map"].fade:
                    self.map.bezier_map["Hole_map"].fade_unselect()
                    # add to history
                    self.map.bezier_map["Hole_map"].add_history("unfade_poly", [])
                    if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                        self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                    if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                        self.undo_but_img.set_img("Icons\\undo_icon_active.png")
                # unselect polygon
                else:
                    # add to history
                    self.map.bezier_map["Hole_map"].add_history("uns_poly", [self.map.bezier_map["Hole_map"].poly_index])
                    if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                        self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                    if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                        self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                    self.map.bezier_map["Hole_map"].unselect_polygon()

    # backspace event
    def backspace(self, event):
        if not self.dis_cha and not self.load_data:
            # delete bezier point
            if self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].edit:
                point_pos = self.map.bezier_map["Hole_map"].points_poly_map[self.map.bezier_map["Hole_map"].poly_index][self.map.bezier_map["Hole_map"].sel_point]
                self.map.bezier_map["Hole_map"].delete_point()
                # add to history
                self.map.bezier_map["Hole_map"].add_history("del_point", [point_pos])
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

            # delete fade curve
            elif self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].fade:
                # add to history
                self.map.bezier_map["Hole_map"].add_history("del_fade", self.map.bezier_map["Hole_map"].pre_adj_fade)
                self.map.bezier_map["Hole_map"].pre_adj_fade = None
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                self.map.bezier_map["Hole_map"].delete_fade()
            # delete polygon
            elif self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].poly_index is not None:
                # add to history
                self.map.bezier_map["Hole_map"].add_history("del_poly", self.map.bezier_map["Hole_map"].get_poly_info())
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                self.map.bezier_map["Hole_map"].delete_polygon()

    # key event
    def key(self, event):
        if not self.dis_cha and not self.load_data:
            # next button press
            if event.char == "n":
                self.next_button_press(shortcut=True)
            # selected
            if self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].poly_index is not None:
                # edit selected
                if event.char == "e":
                    # add to history
                    self.map.bezier_map["Hole_map"].add_history("edi_poly", [])
                    if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                        self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                    if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                        self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                    self.map.bezier_map["Hole_map"].edit_selected()
                # hide selected
                if event.char == "h":
                    # add to history
                    self.map.bezier_map["Hole_map"].add_history("hide_sel", [])
                    if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                        self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                    if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                        self.undo_but_img.set_img("Icons\\undo_icon_active.png")

                    self.map.bezier_map["Hole_map"].hide_selected()
                # fade selected
                if event.char == "f":
                    self.map.bezier_map["Hole_map"].fade_selected()

                    # add to history
                    self.map.bezier_map["Hole_map"].add_history("fade_poly", [])
                    if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                        self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                    if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                        self.undo_but_img.set_img("Icons\\undo_icon_active.png")
                # change fade orientation
                if self.map.bezier_map["Hole_map"].fade_index is not None and event.char == "d":
                    self.map.bezier_map["Hole_map"].change_fade_dir()

            # not selected
            elif self.map.bezier_map_exists("Hole_map") and event.char == "h":
                self.map.bezier_map["Hole_map"].hide_all()
                # add to history
                self.map.bezier_map["Hole_map"].add_history("hide_all", [])
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

    # key pressed
    def keypress(self, event):
        if self.map.bezier_map_exists("Hole_map"):
            # toggle c key_press
            self.map.bezier_map["Hole_map"].c_key_pressed = True
            # change point type
            if self.map.bezier_map["Hole_map"].edit and not self.map.bezier_map["Hole_map"].circle_creation:
                self.map.bezier_map["Hole_map"].change_type()

                # add to history
                self.map.bezier_map["Hole_map"].add_history("cha_point", [])
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

    # key released
    def keyrelease(self, event):
        if event.char == "c":
            # toggle s key released
            if self.map.bezier_map_exists("Hole_map"):
                self.map.bezier_map["Hole_map"].c_key_pressed = False

    # up arrow pressed
    def up(self, event):
        if not self.dis_cha and not self.load_data:
            if self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].poly_index is not None:
                self.map.bezier_map["Hole_map"].up_z_pos()
                # add to history
                self.map.bezier_map["Hole_map"].add_history("up_z", [])
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

    # down arrow pressed
    def down(self, event):
        if not self.dis_cha and not self.load_data:
            if self.map.bezier_map_exists("Hole_map") and self.map.bezier_map["Hole_map"].poly_index is not None:
                self.map.bezier_map["Hole_map"].down_z_pos()
                # add to history
                self.map.bezier_map["Hole_map"].add_history("low_z", [])
                if self.redo_but_img.src == "Icons\\redo_icon_active.png":
                    self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
                if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                    self.undo_but_img.set_img("Icons\\undo_icon_active.png")

    # control z
    def control_z(self, event):
        if not self.dis_cha and not self.load_data:
            if self.map.bezier_map["Hole_map"].history_index == -1:
                self.set_notification("nothing to undo")

            self.map.bezier_map["Hole_map"].undo()

            # update images
            if self.map.bezier_map["Hole_map"].history_index == -1:
                self.undo_but_img.set_img("Icons\\undo_icon_inactive.png")
                self.save_img.set_img("Icons/save_icon_empty.png")
            if self.redo_but_img.src == "Icons\\redo_icon_inactive.png":
                self.redo_but_img.set_img("Icons\\redo_icon_active.png")

    # control shift z
    def control_shift_z(self, event):
        if not self.dis_cha and not self.load_data:
            if self.map.bezier_map["Hole_map"].history_index == len(self.map.bezier_map["Hole_map"].history) - 1:
                self.set_notification("nothing to redo")

            self.map.bezier_map["Hole_map"].redo()

            # update images
            if self.map.bezier_map["Hole_map"].history_index == len(self.map.bezier_map["Hole_map"].history)-1:
                self.redo_but_img.set_img("Icons\\redo_icon_inactive.png")
            if self.undo_but_img.src == "Icons\\undo_icon_inactive.png":
                self.undo_but_img.set_img("Icons\\undo_icon_active.png")
                self.save_img.set_img("Icons/save_icon.png")

    # open the window
    def main_loop(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = GUI()
    gui.main()
    gui.main_loop()
