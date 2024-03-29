import copy
import tkinter as tk
import tkinter.filedialog
from tkinter.font import Font
from Data_visualisation import Data_Visualiser
from skimage.transform import resize
import torch.nn as nn
import numpy as np
import PIL as pil
from PIL import ImageTk
import os
import torch
import threading
from Canvas_Objects import *
import cv2


class Playground(object):
    def __init__(self):
        self.WINDOW_SIZE = [1424, 801]

        # create Window
        self.root = tk.Tk()
        self.root.geometry(f"{self.WINDOW_SIZE[0]}x{self.WINDOW_SIZE[1]}")

        # create Canvas
        self.canvas = tk.Canvas(self.root, height=self.WINDOW_SIZE[0], width=self.WINDOW_SIZE[0], bg="#DCDCDC")
        self.canvas.place(x=-2, y=-2)

        # data visualiser
        self.visualiser = Data_Visualiser(image_size=(66, 128), box_size=4)

        self.model = Generator()
        self.model_loaded = False
        # create model selection
        self.model_sel_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 255, 10],
                                        [self.WINDOW_SIZE[0] // 2 + 255, 60], 10, [240, 240, 240], 0, [0, 0, 0])
        self.model_sel_folder_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 + 95, 10],
                                               [self.WINDOW_SIZE[0] // 2 + 145, 60], 10, [240, 240, 240], 0, [0, 0, 0])
        img = pil.ImageTk.PhotoImage(pil.Image.open("Icons/folder.png"))
        self.model_sel_folder_img = Image(self.canvas, img, [self.WINDOW_SIZE[0] // 2 + 120, 35])
        self.model_sel_model_label = Text(self.canvas, "Select Model", [self.WINDOW_SIZE[0] // 2 - 235, 35],
                                          [25, 25, 25], font_size=20, anchor=tk.W)
        self.model_sel_gener_label = Text(self.canvas, "Generate image", [self.WINDOW_SIZE[0] // 2 - 235, 30],
                                          [240, 240, 240], font_size=20, anchor=tk.W)
        self.image_save_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 + 155, 10],
                                         [self.WINDOW_SIZE[0] // 2 + 255, 60], 10, [240, 240, 240], 0, [0, 0, 0])
        img = pil.ImageTk.PhotoImage(pil.Image.open("Icons/bild.png"))
        self.save_image_img = Image(self.canvas, img, [self.WINDOW_SIZE[0] // 2 + 180, 35])
        img = pil.ImageTk.PhotoImage(pil.Image.open("Icons/video.png"))
        self.save_video_img = Image(self.canvas, img, [self.WINDOW_SIZE[0] // 2 + 230, 35])

        # probability toggle
        self.probability = False
        self.prob_label = Text(self.canvas, "Probability", [29, 60], [150, 150, 150], font_size=16, anchor=tk.W)
        self.prob_indi = Rectangle(self.canvas, [10, 53], [23, 66], 3, [220, 220, 220], 1, [150, 150, 150])
        # auto generate toggle
        self.auto_gen = False
        self.auto_gen_label = Text(self.canvas, "Auto generate", [179, 60], [150, 150, 150], font_size=16, anchor=tk.W)
        self.auto_gen_indi = Rectangle(self.canvas, [160, 53], [173, 66], 3, [220, 220, 220], 1, [150, 150, 150])

        # generated image
        self.images_prob = {}
        self.images = {"Placeholder": np.asarray(pil.Image.open("Icons/Golf_hole_placeholder.png"))}
        self.image_key = "Placeholder"
        self.generated_image = Image(self.canvas, None, [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2])
        self.visualise_generated_image()

        # latent menu
        self.latent_menu = False
        self.y_scroll = 0
        self.new_slider_pos = 0
        self.latent_label_back = Rectangle(self.canvas, [-320, 0], [0, 75], 0, [220, 220, 220], 0, [220, 220, 220])
        self.latent_label = Text(self.canvas, "Latent Menu", [-160, 25], [150, 150, 150], 17, anchor=tk.CENTER)
        self.latent_border_line = Line(self.canvas, [0, 0], [0, 2000], [180, 180, 180], 1)
        self.latent_toggle_back = Rectangle(self.canvas, [0, 0], [50, 50], 0, [220, 220, 220], 0, [220, 220, 220])
        self.latent_toggle_l1 = Line(self.canvas, [15, 22], [35, 22], [150, 150, 150], 1)
        self.latent_toggle_l2 = Line(self.canvas, [15, 28], [35, 28], [150, 150, 150], 1)
        self.new_slider_back = Rectangle(self.canvas, [-320, 75], [-20, 115], 10, [240, 240, 240], 0, [240, 240, 240])
        self.new_slider_label = Text(self.canvas, "Add new slider", [-160, 95], [0, 0, 0], 15, anchor=tk.CENTER)
        self.latent_sliders = {}

        self.edit_slider = False
        self.edit_slider_key = None
        self.edit_indication_line = Line(self.canvas, [0, 0], [0, 0], [0, 0, 0], 1)

        # animation menu
        self.current_time_step = 0
        self.max_time_steps = 250
        self.run_time = False

        self.time_play_button_1 = Polygon(self.canvas, [[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]], [150, 150, 150], 0, [150, 150, 150])
        self.time_play_button_2 = Polygon(self.canvas, [[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]], [150, 150, 150], 0, [150, 150, 150])
        self.time_step_line = Line(self.canvas, [self.WINDOW_SIZE[0] - 25, 50], [self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 50], [150, 150, 150], 1)
        self.time_step_indication = Circle(self.canvas, [self.WINDOW_SIZE[0] - 25, (self.WINDOW_SIZE[1] - 100) / self.max_time_steps * self.current_time_step + 50], 3, [150, 150, 150], 0, [150, 150, 150])
        self.time_step_label = Text(self.canvas, f"{self.current_time_step}", [self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 33], [150, 150, 150], 12)
        self.max_time_step_label = Text(self.canvas, f"{self.max_time_steps}", [self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 17], [50, 50, 50], 12)

        self.key_frame_indicator = []
        self.animation_functions = []

        self.time_line_pressed = False
        self.time_step_selected = False
        self.max_time_steps_selected = False
        self.edit_time_line = Line(self.canvas, [0, 0], [0, 0], [0, 0, 0], 1)

        # save popup_menu
        self.save_ppm = False
        self.save_ppm_mode = "Image"
        self.save_ppm_path = "Playground Images and Videos"
        self.save_ppm_img_name = "Image 1"
        self.save_ppm_start_frame = 0
        self.save_ppm_end_frame = 250
        self.save_ppm_render = False
        self.save_ppm_render_progress = 0
        self.save_ppm_terminate_render = False
        self.save_ppm_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 150, self.WINDOW_SIZE[1] // 2 - 200], [self.WINDOW_SIZE[0] // 2 + 150, self.WINDOW_SIZE[1] // 2 + 200], 10, [240, 240, 240], 0, [0, 0, 0])
        self.save_ppm_title = Text(self.canvas, "Save Image", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 175], [0, 0, 0], 18, anchor=tk.W)
        self.save_ppm_exit_cross_l1 = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 + 118, self.WINDOW_SIZE[1] // 2 - 168], [self.WINDOW_SIZE[0] // 2 + 133, self.WINDOW_SIZE[1] // 2 - 183], [150, 150, 150], 1)
        self.save_ppm_exit_cross_l2 = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 + 118, self.WINDOW_SIZE[1] // 2 - 182], [self.WINDOW_SIZE[0] // 2 + 133, self.WINDOW_SIZE[1] // 2 - 167], [150, 150, 150], 1)
        self.save_ppm_name_label = Text(self.canvas, "Image name:", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 88], [0, 0, 0], 12, anchor=tk.NW)
        self.save_ppm_name_underline = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 43], [self.WINDOW_SIZE[0] // 2 + 125, self.WINDOW_SIZE[1] // 2 - 43], [200, 200, 200], 1)
        self.save_ppm_name_text = Text(self.canvas, self.save_ppm_img_name, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 44], [200, 200, 200], 12, anchor=tk.SW)
        self.save_ppm_name_entry = tk.Entry(self.root, font=("Arial", -12), fg="black", bg="#f0f0f0", bd=0)
        self.save_ppm_dir_label = Text(self.canvas, "Save location:", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 27], [0, 0, 0], 12, anchor=tk.NW)
        img = pil.ImageTk.PhotoImage(pil.Image.open("Icons/ppm_folder.png"))
        self.save_ppm_dir_folder = Image(self.canvas, img, [self.WINDOW_SIZE[0] // 2 + 113, self.WINDOW_SIZE[1] // 2 - 20])
        self.save_ppm_dir_underline = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 10], [self.WINDOW_SIZE[0] // 2 + 100, self.WINDOW_SIZE[1] // 2 - 10], [200, 200, 200], 1)
        self.save_ppm_dir_text = Text(self.canvas, "Playground Images and Videos", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 11], [200, 200, 200], 12, anchor=tk.SW)
        self.save_ppm_dir_entry = tk.Entry(self.root, font=("Arial", -12), fg="black", bg="#f0f0f0", bd=0)
        self.save_ppm_size_label = Text(self.canvas, "Resolution:", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 + 10], [0, 0, 0], 12, anchor=tk.NW)
        self.save_ppm_size_underline_1 = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 + 55], [self.WINDOW_SIZE[0] // 2 - 10, self.WINDOW_SIZE[1] // 2 + 55], [200, 200, 200], 1)
        self.save_ppm_size_underline_2 = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 + 125, self.WINDOW_SIZE[1] // 2 + 55], [self.WINDOW_SIZE[0] // 2 + 10, self.WINDOW_SIZE[1] // 2 + 55], [200, 200, 200], 1)
        self.save_ppm_size_divider = Text(self.canvas, "x", [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2 + 55], [200, 200, 220], 12, anchor=tk.S)
        self.save_ppm_width_label = Text(self.canvas, "66", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 + 54], [200, 200, 220], 12, anchor=tk.SW)
        self.save_ppm_width_entry = tk.Entry(self.root, font=("Arial", -12), fg="black", bg="#f0f0f0", bd=0)
        self.save_ppm_height_label = Text(self.canvas, "128", [self.WINDOW_SIZE[0] // 2 + 10, self.WINDOW_SIZE[1] // 2 + 54], [200, 200, 220], 12, anchor=tk.SW)
        self.save_ppm_height_entry = tk.Entry(self.root, font=("Arial", -12), fg="black", bg="#f0f0f0", bd=0)
        self.save_ppm_frame_label = Text(self.canvas, "Frame range:", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 + 75], [0, 0, 0], 12, anchor=tk.NW)
        self.save_ppm_frame_underline_1 = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 + 55], [self.WINDOW_SIZE[0] // 2 - 10, self.WINDOW_SIZE[1] // 2 + 55], [200, 200, 200], 1)
        self.save_ppm_frame_underline_2 = Line(self.canvas, [self.WINDOW_SIZE[0] // 2 + 125, self.WINDOW_SIZE[1] // 2 + 55], [self.WINDOW_SIZE[0] // 2 + 10, self.WINDOW_SIZE[1] // 2 + 55], [200, 200, 200], 1)
        self.save_ppm_frame_divider = Text(self.canvas, "to", [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2 + 55], [200, 200, 220], 12, anchor=tk.S)
        self.save_ppm_sframe_label = Text(self.canvas, "0", [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 + 54], [200, 200, 220], 12, anchor=tk.SW)
        self.save_ppm_sframe_entry = tk.Entry(self.root, font=("Arial", -12), fg="black", bg="#f0f0f0", bd=0)
        self.save_ppm_eframe_label = Text(self.canvas, "250", [self.WINDOW_SIZE[0] // 2 + 10, self.WINDOW_SIZE[1] // 2 + 54], [200, 200, 220], 12, anchor=tk.SW)
        self.save_ppm_eframe_entry = tk.Entry(self.root, font=("Arial", -12), fg="black", bg="#f0f0f0", bd=0)
        self.save_ppm_progress_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 + 125, self.WINDOW_SIZE[1] // 2 + 12], 6, [200, 200, 200], 0, [0, 0, 0])
        self.save_ppm_progress_bar = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 - 117, self.WINDOW_SIZE[1] // 2 + 12], 6, [73, 182, 91], 0, [0, 0, 0])
        self.save_ppm_progress_label = Text(self.canvas, "0 / 250", [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2], [255, 255, 255], 12)
        # self.save_ppm_range_label
        self.save_ppm_save_button_cover = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 150, self.WINDOW_SIZE[1] // 2 + 140], [self.WINDOW_SIZE[0] // 2 + 150, self.WINDOW_SIZE[1] // 2 + 150], 0, [240, 240, 240], 0, [0, 0, 0])
        self.save_ppm_save_button = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 150, self.WINDOW_SIZE[1] // 2 + 140], [self.WINDOW_SIZE[0] // 2 + 150, self.WINDOW_SIZE[1] // 2 + 200], 10, [73, 182, 91], 0, [0, 0, 0])
        self.save_ppm_save_label = Text(self.canvas, "Save", [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2 + 175], [255, 255, 255], 18)

        # create random latent space
        self.latent_space = torch.randn(1, 100, 1, 1)
        self.latent_space /= torch.max(torch.abs(self.latent_space))
        self.latent_vis = [Rectangle(self.canvas, [0, 0], [0, 0], 0, [150, 150, 150], 0, [0, 0, 0]) for i in range(100)]

        self.create_new_slider()
        self.create_new_slider()
        self.create_new_slider()

        self.slider_pressed = None
        self.last_click_pos = []

        # bind events
        self.canvas.bind('<Button-1>', self.button_1)
        self.canvas.bind('<B1-Motion>', self.button_1_motion)
        self.canvas.bind('<ButtonRelease-1>', self.button_1_release)
        self.canvas.bind('<MouseWheel>', self.mouse_wheel)
        self.root.bind('<Key>', self.key)
        self.root.bind_class("Tk", "<Configure>", self.resize)

    def draw(self):
        # draw generated image
        self.generated_image.draw()

        # draw model selection
        self.model_sel_folder_back.draw()
        self.image_save_back.draw()
        self.model_sel_folder_img.draw()
        self.save_image_img.draw()
        self.save_video_img.draw()
        self.model_sel_back.draw()
        self.model_sel_model_label.draw()

        # draw latent menu
        self.latent_label_back.draw()
        self.latent_label.draw()
        self.latent_border_line.draw()
        self.latent_toggle_back.draw()
        self.latent_toggle_l1.draw()
        self.latent_toggle_l2.draw()
        self.new_slider_back.draw()
        self.new_slider_label.draw()

        # draw toggles
        self.prob_label.draw()
        self.prob_indi.draw()
        self.auto_gen_label.draw()
        self.auto_gen_indi.draw()

        # draw animation menu
        self.time_step_line.draw()
        self.time_step_indication.draw()
        self.time_play_button_1.draw()
        self.time_play_button_1.draw()
        self.time_step_label.draw()
        self.max_time_step_label.draw()

        self.visualise_latent()

    def set_time_step(self, new_time_step: int, animation: bool = False, animation_time: float = None):
        new_time_step -= self.max_time_steps if new_time_step > self.max_time_steps else 0

        # update latent values
        for keyframes in self.animation_functions:
            index = keyframes[0]
            function = None
            function_start = None
            for key in keyframes[1:]:
                if key[0] <= new_time_step:
                    function = key[1]
                    function_start = key[0]
                else:
                    break

            self.latent_space[0, index, 0, 0] = function(new_time_step - function_start)

        # set visuals
        self.time_step_indication.set_center([self.WINDOW_SIZE[0] - 25, (self.WINDOW_SIZE[1] - 100) / self.max_time_steps * self.current_time_step + 50], animation=animation, animation_time=animation_time)
        self.time_step_label.set_text(f"{new_time_step}")

        self.generate_image(set_as_vis=True)

        self.visualise_latent()
        self.update_slider_pos([10 if self.latent_menu else -320, 75])

        # update time step variable
        self.current_time_step = new_time_step

    def visualise_latent(self, animation=False, animation_time=0.2):
        # normalize values
        values = self.latent_space.squeeze().tolist()

        # calculate cube width
        side_spacing = floor(2 + (self.WINDOW_SIZE[0] - (4 * 100 + 4)) / 2)

        # calculate bar positions
        for i, (val, widget) in enumerate(zip(values, self.latent_vis)):
            # up bars
            if val >= 0:
                widget.set_pos([side_spacing + i * 4 + 1, self.WINDOW_SIZE[1] - 23 - val * 20],
                               [side_spacing + (i + 1) * 4 - 1, self.WINDOW_SIZE[1] - 23], animation=animation, animation_time=animation_time)
            # down bars
            else:
                widget.set_pos([side_spacing + i * 4 + 1, self.WINDOW_SIZE[1] - 23],
                               [side_spacing + (i + 1) * 4 - 1, self.WINDOW_SIZE[1] - 23 - val * 20], animation=animation, animation_time=animation_time)

    def run_animation(self):
        # move on
        if self.run_time and self.current_time_step + 1 <= self.max_time_steps:
            self.set_time_step(self.current_time_step + 1)

            self.canvas.after(16, self.run_animation)
        # pause animation
        elif self.run_time:
            self.run_time = False
            self.time_play_button_1.set_points([[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]], animation=True, animation_time=0.1)
            self.time_play_button_2.set_points([[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]], animation=True, animation_time=0.1)

    def calculate_animation_functions(self):
        # create index list
        indexes = []
        values = []
        for key_frame in self.key_frame_indicator:
            for j, i in enumerate(key_frame[1]):
                if not indexes.count(i):
                    indexes.append(i)
                    values.append([[key_frame[0], key_frame[2][j]]])
                else:
                    values[indexes.index(i)].append([key_frame[0], key_frame[2][j]])

        self.animation_functions.clear()
        # create animation functions
        for vals_i, vals in enumerate(values):
            self.animation_functions.append([indexes[vals_i]])
            if len(vals) > 1:
                for val_i, val in enumerate(vals[:-1]):
                    # function to first keyframe
                    if val_i == 0 and val[0] > 0:
                        self.animation_functions[-1].append([0, lambda t, val=val: val[1]])

                    # ease function
                    start = val[1]
                    ran = vals[val_i + 1][1] - val[1]
                    animation_length = vals[val_i + 1][0] - val[0]
                    self.animation_functions[-1].append([val[0], lambda t, start=start, ran=ran,
                                                         animation_length=animation_length: (sin(t * (pi / animation_length) - (pi / 2)) + 1) * ran / 2 + start])

                    # function from last keyframe
                    if val_i == len(vals) - 2 and vals[-1][0] < self.max_time_steps:
                        self.animation_functions[-1].append([vals[-1][0], lambda t, vals=vals: vals[-1][1]])

            else:
                self.animation_functions[-1].append([0, lambda t, vals=vals: vals[0][1]])

    # reset sliders
    def reset_slider(self):
        if self.edit_slider:
            # reset visuals
            self.latent_sliders[self.edit_slider_key[0]][1].set_color([205, 205, 205])
            self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(self.edit_slider_key[0]))
            # reset variables
            self.edit_slider = False
            self.edit_slider_key = None
            self.edit_indication_line.delete()

    def reset_animation_entries(self):
        self.time_step_selected = False
        self.max_time_steps_selected = False

        self.edit_time_line.delete()

    # left click
    def button_1(self, event):
        self.last_click_pos = [event.x, event.y]
        self.reset_slider()
        self.reset_animation_entries()
        if self.save_ppm and not self.save_ppm_render and not (not self.save_ppm_back.is_pressed(event.x, event.y) or 250 <= event.x - self.WINDOW_SIZE[0] // 2 + 150 <= 300 and event.y - self.WINDOW_SIZE[1] // 2 + 200 <= 50):
            self.reset_ppm_entrys()

        # select model
        if not self.save_ppm:
            if (self.model_sel_back.is_pressed(event.x, event.y) and self.model_sel_model_label.text == "Select Model") or \
                    self.model_sel_folder_back.is_pressed(event.x, event.y):
                # clear images
                placeholder = self.images["Placeholder"]
                self.images.clear()
                self.images.update({"Placeholder": placeholder})
                self.image_key = "Placeholder"

                # load model
                model = tk.filedialog.askopenfilename(initialdir="Model Data/Models",
                                                      filetypes=(("Models", "Generator*.pth"), ("all files", "*.*")))
                # define Model name
                if model != "":
                    if model.split("/")[-2] == "Backups":
                        name = f"{model.split('/')[-3].split('. ')[-1]} - {model.split('/')[-1].split('_')[-1].replace('.pth', '')}"
                    else:
                        name = model.split('/')[-2].split('. ')[-1]
                    # Update GUI
                    self.model_sel_model_label.set_text(os.path.basename(name))

                    # Button convert animation
                    if not self.model_loaded:
                        self.model_sel_gener_label.draw()
                        self.model_sel_model_label.set_color([122, 233, 142], animation=True, animation_time=0.2)
                        self.model_sel_model_label.set_center([self.WINDOW_SIZE[0] // 2 - 235, 46], animation=True,
                                                              animation_time=0.2)
                        self.model_sel_model_label.set_font_size(11, animation=True, animation_time=0.2)
                        self.model_sel_back.set_pos([self.WINDOW_SIZE[0] // 2 - 255, 10],
                                                    [self.WINDOW_SIZE[0] // 2 + 85, 60],
                                                    animation=True, animation_time=0.2)
                        self.model_sel_back.set_color([73, 182, 91], animation=True, animation_time=0.2)

                        self.model_loaded = True

                    # load model
                    thread = threading.Thread(target=lambda: self.load_model(model))
                    self.canvas.after(200, lambda: thread.start())

            # generate image
            elif self.model_sel_back.is_pressed(event.x, event.y) and self.model_sel_model_label.text != "Select Model":
                thread = threading.Thread(target=lambda: self.generate_image(set_as_vis=True))
                thread.start()

            # probability toggle pressed
            elif self.prob_indi.is_pressed(event.x, event.y):
                # turn probability off
                if self.probability:
                    self.probability = False
                    self.prob_indi.set_color([220, 220, 220], animation=True, animation_time=0.2)
                    self.prob_indi.set_outline_color([150, 150, 150], animation=True, animation_time=0.2)
                # turn probability on
                else:
                    self.probability = True
                    self.prob_indi.set_color([73, 182, 91], animation=True, animation_time=0.2)
                    self.prob_indi.set_outline_color([73, 182, 91], animation=True, animation_time=0.2)

                # visualise generated image
                self.visualise_generated_image()

            # auto generation toggle pressed
            elif self.auto_gen_indi.is_pressed(event.x, event.y):
                # turn probability off
                if self.auto_gen:
                    self.auto_gen = False
                    self.auto_gen_indi.set_color([220, 220, 220], animation=True, animation_time=0.2)
                    self.auto_gen_indi.set_outline_color([150, 150, 150], animation=True, animation_time=0.2)
                # turn probability on
                else:
                    self.auto_gen = True
                    self.auto_gen_indi.set_color([73, 182, 91], animation=True, animation_time=0.2)
                    self.auto_gen_indi.set_outline_color([73, 182, 91], animation=True, animation_time=0.2)

            # add new slider pressed
            elif self.new_slider_back.is_pressed(event.x, event.y):
                self.create_new_slider()

            # latent menu toggle pressed
            elif 10 < event.x < 40 and 10 < event.y < 40:
                # open latent menu
                if not self.latent_menu:
                    # animate menu components
                    self.latent_label_back.set_pos([0, 0], [320, 75], animation=True, animation_time=0.2)
                    self.latent_label.set_center([160, 25], animation=True, animation_time=0.2)
                    self.latent_border_line.set_pos([320, 0], [320, 2000], animation=True, animation_time=0.2)
                    self.latent_toggle_l1.set_pos([18, 18], [33, 33], animation=True, animation_time=0.2)
                    self.latent_toggle_l2.set_pos([18, 32], [33, 17], animation=True, animation_time=0.2)
                    self.new_slider_back.set_pos([10, self.new_slider_pos * 92 + 75 + self.y_scroll], [310, self.new_slider_pos * 92 + 115 + self.y_scroll], animation=True, animation_time=0.2)
                    self.new_slider_label.set_center([160, self.new_slider_pos * 92 + 95 + self.y_scroll], animation=True, animation_time=0.2)

                    self.latent_menu = True

                    self.update_slider_pos([10, 75], animation=True, animation_time=0.2)
                # close latent menu
                else:
                    # animate menu components
                    self.latent_label_back.set_pos([-320, 0], [0, 75], animation=True, animation_time=0.2)
                    self.latent_label.set_center([-160, 25], animation=True, animation_time=0.2)
                    self.latent_border_line.set_pos([0, 0], [0, 2000], animation=True, animation_time=0.2)
                    self.latent_toggle_l1.set_pos([15, 22], [35, 22], animation=True, animation_time=0.2)
                    self.latent_toggle_l2.set_pos([15, 28], [35, 28], animation=True, animation_time=0.2)
                    self.new_slider_back.set_pos([-310, self.new_slider_pos * 92 + 75 + self.y_scroll], [-10, self.new_slider_pos * 92 + 115 + self.y_scroll], animation=True, animation_time=0.2)
                    self.new_slider_label.set_center([-160, self.new_slider_pos * 92 + 95 + self.y_scroll], animation=True, animation_time=0.2)

                    self.latent_menu = False

                    self.update_slider_pos([-320, 75], animation=True, animation_time=0.2)

            # latent space vis pressed
            elif -200 <= event.x - self.WINDOW_SIZE[0] // 2 <= 200 and self.WINDOW_SIZE[1] - event.y <= 50:
                self.latent_space = torch.randn(1, 100, 1, 1)
                self.latent_space /= torch.max(torch.abs(self.latent_space))

                self.visualise_latent(animation=True, animation_time=0.2)

                # update latent sliders
                for i, key in enumerate(self.latent_sliders.keys()):
                    value = float(self.latent_space[0, int(key), 0, 0])
                    top_left = [10 if self.latent_menu else -320, 133 + 92 * i + self.y_scroll]
                    self.latent_sliders[key][5].set_center([top_left[0] + 162 + value * 132, top_left[1]], animation=True, animation_time=0.2)

                # update image
                if self.model_loaded:
                    thread = threading.Thread(target=lambda: self.generate_image(set_as_vis=True))
                    self.canvas.after(200, lambda: thread.start())

            # latent slider presses
            elif self.latent_menu and 10 <= event.x <= 310:
                for i, key in enumerate(self.latent_sliders.keys()):
                    # slider heading press
                    if 75 + 92 * i + self.y_scroll <= event.y <= 111 + 92 * i + self.y_scroll:
                        # delete
                        if 264 <= event.x:
                            self.delete_slider(key, menu_open=True)
                        # change index
                        else:
                            # turn on edit mode
                            self.edit_slider = True
                            self.edit_slider_key = [key, i]
                            # create indication label
                            text_length = Font(family="Arial", size=-25).measure(key)
                            self.edit_indication_line.set_pos(
                                [160 + text_length / 2, 81 + 92 * i + self.y_scroll],
                                [160 + text_length / 2, 105 + 92 * i + self.y_scroll])
                            self.edit_indication_line.draw()

                            # raise tags
                            self.canvas.tag_raise(self.latent_label_back.object)
                            self.canvas.tag_raise(self.latent_label.object)
                            self.canvas.tag_raise(self.latent_toggle_back.object)
                            self.canvas.tag_raise(self.latent_toggle_l1.object)
                            self.canvas.tag_raise(self.latent_toggle_l2.object)
                            self.canvas.tag_raise(self.prob_indi.object)
                            self.canvas.tag_raise(self.prob_label.object)
                            self.canvas.tag_raise(self.auto_gen_indi.object)
                            self.canvas.tag_raise(self.auto_gen_label.object)

                        break

                    # slider point press
                    elif self.latent_sliders[key][5].is_pressed(event.x, event.y):
                        self.slider_pressed = [i, key]

            # start or pause animation
            elif self.WINDOW_SIZE[0] - 40 <= event.x <= self.WINDOW_SIZE[0] - 10 and 10 <= event.y <= 40:
                if not self.run_time:
                    self.run_time = True
                    self.time_play_button_1.set_points([[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 27, 18], [self.WINDOW_SIZE[0] - 27, 32], [self.WINDOW_SIZE[0] - 31, 32]], animation=True, animation_time=0.1)
                    self.time_play_button_2.set_points([[self.WINDOW_SIZE[0] - 23, 18], [self.WINDOW_SIZE[0] - 19, 18], [self.WINDOW_SIZE[0] - 19, 32], [self.WINDOW_SIZE[0] - 23, 32]], animation=True, animation_time=0.1)

                    self.run_animation()
                else:
                    self.run_time = False
                    self.time_play_button_1.set_points([[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]], animation=True, animation_time=0.1)
                    self.time_play_button_2.set_points([[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]], animation=True, animation_time=0.1)

            # set time step
            elif self.WINDOW_SIZE[0] - 30 <= event.x <= self.WINDOW_SIZE[0] - 20 and 45 <= event.y <= self.WINDOW_SIZE[1] - 45:
                self.current_time_step = round((event.y - 50) / (self.WINDOW_SIZE[1] - 100) * self.max_time_steps)
                self.current_time_step = 0 if self.current_time_step < 0 else self.max_time_steps if self.current_time_step > self.max_time_steps else self.current_time_step

                self.set_time_step(self.current_time_step)
                self.time_line_pressed = True

            # select current time step label
            elif self.WINDOW_SIZE[0] - 50 <= event.x and self.WINDOW_SIZE[1] - 40 <= event.y <= self.WINDOW_SIZE[1] - 25:
                self.time_step_selected = True

                x = self.time_step_label.font.measure(f"{self.current_time_step}") / 2 + self.WINDOW_SIZE[0] - 25
                self.edit_time_line.set_pos([x, self.WINDOW_SIZE[1] - 39], [x, self.WINDOW_SIZE[1] - 26])
            # select max time steps label
            elif self.WINDOW_SIZE[0] - 50 <= event.x and self.WINDOW_SIZE[1] - 25 <= event.y <= self.WINDOW_SIZE[1] - 10:
                self.max_time_steps_selected = True

                x = self.max_time_step_label.font.measure(f"{self.max_time_steps}") / 2 + self.WINDOW_SIZE[0] - 25
                self.edit_time_line.set_pos([x, self.WINDOW_SIZE[1] - 23], [x, self.WINDOW_SIZE[1] - 11])

            # save image / video
            elif self.image_save_back.is_pressed(event.x, event.y) and self.model_loaded:
                if event.x <= self.WINDOW_SIZE[0] // 2 + 205:
                    self.save_ppm_mode = "Image"
                    self.open_save_ppm()
                else:
                    self.save_ppm_mode = "Video"
                    self.open_save_ppm()

        # save ppm open
        elif not self.save_ppm_render:
            center = [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2 if self.save_ppm_mode == "Image" else self.WINDOW_SIZE[1] // 2 - 33]
            # name
            if 25 <= event.x - center[0] + 150 <= 250 and 141 <= event.y - center[1] + 200 <= 153:
                # visualise entry
                self.save_ppm_name_entry.insert(0, self.save_ppm_img_name)
                self.save_ppm_name_entry.place(x=center[0] - 128, y=center[1] - 66, width=250)
                self.save_ppm_name_entry.focus_set()
    
                # set cursor position
                for i in range(len(self.save_ppm_name_text.text)):
                    if self.save_ppm_name_text.font.measure(self.save_ppm_name_text.text[:i]) > event.x - center[0] + 125:
                        self.save_ppm_name_entry.icursor(i - 1)
                        break
                        
            # dir
            elif 25 <= event.x - center[0] + 150 <= 250 and 206 <= event.y - center[1] + 200 <= 218:
                # visualise entry
                self.save_ppm_dir_entry.insert(0, self.save_ppm_path)
                self.save_ppm_dir_entry.place(x=center[0] - 128, y=center[1] - 1, width=225)
                self.save_ppm_dir_entry.focus_set()

                # set cursor position
                for i in range(len(self.save_ppm_dir_text.text)):
                    if self.save_ppm_dir_text.font.measure(self.save_ppm_dir_text.text[:i]) > event.x - center[0] + 125:
                        self.save_ppm_dir_entry.icursor(i - 1)
                        break

            # folder button
            elif 250 <= event.x - center[0] + 150 <= 275 and 193 <= event.y - center[1] + 200 <= 218:
                path = self.save_ppm_path if self.save_ppm_dir_underline.color == [200, 200, 200] else f"Playground Images and Videos"
                path = tk.filedialog.askdirectory(initialdir=path)
                if path != "":
                    self.save_ppm_path = path

                    if self.save_ppm_dir_text.font.measure(text := path) > 225:
                        for i in range(len(text)):
                            if self.save_ppm_dir_text.font.measure(text[:i] + "...") > 225:
                                text = text[:i - 1] + "..."
                                break

                    self.save_ppm_dir_text.set_text(text)

                    # update underline color to indicate error
                    if os.path.exists(self.save_ppm_path) and os.path.isdir(self.save_ppm_path):
                        self.save_ppm_dir_underline.set_color([200, 200, 200])

                        # update name underline color
                        file_path = os.path.join(self.save_ppm_path, self.save_ppm_img_name + ".png")
                        if os.path.isfile(file_path):
                            self.save_ppm_name_underline.set_color([215, 64, 64])
                        else:
                            self.save_ppm_name_underline.set_color([200, 200, 200])
                    else:
                        self.save_ppm_dir_underline.set_color([215, 64, 64])
                        self.save_ppm_name_underline.set_color([200, 200, 200])

            # width
            elif 25 <= event.x - center[0] + 150 <= 140 and 271 <= event.y - center[1] + 200 <= 283:
                # visualise entry
                self.save_ppm_width_entry.insert(0, self.save_ppm_width_label.text)
                self.save_ppm_width_entry.place(x=center[0] - 128, y=center[1] + 64, width=115)
                self.save_ppm_width_entry.focus_set()

                # set cursor position
                for i in range(len(self.save_ppm_width_label.text)):
                    if self.save_ppm_width_label.font.measure(self.save_ppm_width_label.text[:i]) > event.x - center[0] + 125:
                        self.save_ppm_width_entry.icursor(i - 1)
                        break
            
            # height
            elif 160 <= event.x - center[0] + 150 <= 275 and 271 <= event.y - center[1] + 200 <= 283:
                # visualise entry
                self.save_ppm_height_entry.insert(0, self.save_ppm_height_label.text)
                self.save_ppm_height_entry.place(x=center[0] + 7, y=center[1] + 64, width=115)
                self.save_ppm_height_entry.focus_set()

                # set cursor position
                for i in range(len(self.save_ppm_height_label.text)):
                    if self.save_ppm_height_label.font.measure(self.save_ppm_height_label.text[:i]) > event.x - center[0] - 10:
                        self.save_ppm_height_entry.icursor(i - 1)
                        break

            # start frame
            elif self.save_ppm_mode == "Video" and 25 <= event.x - center[0] + 150 <= 150 and 336 <= event.y - center[1] + 200 <= 348:
                # visualise entry
                self.save_ppm_sframe_entry.insert(0, self.save_ppm_sframe_label.text)
                self.save_ppm_sframe_entry.place(x=center[0] - 128, y=center[1] + 129, width=115)
                self.save_ppm_sframe_entry.focus_set()

                # set cursor position
                for i in range(len(self.save_ppm_sframe_label.text)):
                    if self.save_ppm_sframe_label.font.measure(self.save_ppm_sframe_label.text[:i]) > event.x - center[0] + 125:
                        self.save_ppm_sframe_entry.icursor(i - 1)
                        break
            
            # end frame
            elif self.save_ppm_mode == "Video" and 160 <= event.x - center[0] + 150 <= 275 and 336 <= event.y - center[1] + 200 <= 348:
                # visualise entry
                self.save_ppm_eframe_entry.insert(0, self.save_ppm_eframe_label.text)
                self.save_ppm_eframe_entry.place(x=center[0] + 7, y=center[1] + 129, width=115)
                self.save_ppm_eframe_entry.focus_set()

                # set cursor position
                for i in range(len(self.save_ppm_eframe_label.text)):
                    if self.save_ppm_eframe_label.font.measure(self.save_ppm_eframe_label.text[:i]) > event.x - center[0] - 10:
                        self.save_ppm_eframe_entry.icursor(i - 1)
                        break

            # exit
            elif not self.save_ppm_back.is_pressed(event.x, event.y) or 250 <= event.x - center[0] + 150 <= 300 and event.y - self.WINDOW_SIZE[1] // 2 + 200 <= 50:
                self.close_save_popup()

            # save image
            elif self.save_ppm_save_button.is_pressed(event.x, event.y) and 150 <= event.y - self.WINDOW_SIZE[1] // 2 + 200 and self.save_ppm_save_button.color != [200, 200, 200]:
                # save image
                if self.save_ppm_mode == "Image":
                    width = int(self.save_ppm_width_label.text)
                    height = int(self.save_ppm_height_label.text)
                    path = os.path.join(self.save_ppm_path + "/", self.save_ppm_img_name + ".png")

                    image = resize(self.images[str(self.latent_space.squeeze().tolist())], (height, width), order=0,
                                   mode='constant', anti_aliasing=False)

                    image = image.astype(np.uint8)
                    pil_img = pil.Image.fromarray(image, mode="RGB")
                    pil_img.save(path)

                    self.close_save_popup()
                # save video
                else:
                    width = int(self.save_ppm_width_label.text)
                    height = int(self.save_ppm_height_label.text)
                    path = os.path.join(self.save_ppm_path + "/", self.save_ppm_img_name + ".avi")

                    self.save_ppm_render = True

                    # delete content
                    self.save_ppm_exit_cross_l1.delete()
                    self.save_ppm_exit_cross_l2.delete()
                    self.save_ppm_name_label.delete()
                    self.save_ppm_name_underline.delete()
                    self.save_ppm_name_text.delete()
                    self.save_ppm_dir_label.delete()
                    self.save_ppm_dir_folder.delete()
                    self.save_ppm_dir_underline.delete()
                    self.save_ppm_dir_text.delete()
                    self.save_ppm_size_label.delete()
                    self.save_ppm_size_underline_1.delete()
                    self.save_ppm_size_underline_2.delete()
                    self.save_ppm_size_divider.delete()
                    self.save_ppm_width_label.delete()
                    self.save_ppm_height_label.delete()
                    self.save_ppm_frame_label.delete()
                    self.save_ppm_frame_underline_1.delete()
                    self.save_ppm_frame_underline_2.delete()
                    self.save_ppm_frame_divider.delete()
                    self.save_ppm_sframe_label.delete()
                    self.save_ppm_eframe_label.delete()

                    self.save_ppm_title.set_text("Render video")
                    self.save_ppm_save_button.set_color([200, 200, 200])
                    self.save_ppm_save_label.set_text("Cancel")

                    self.save_ppm_progress_back.draw()
                    self.save_ppm_progress_bar.draw()
                    self.save_ppm_progress_label.draw()

                    self.save_ppm_progress_back.set_pos([self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 + 125, self.WINDOW_SIZE[1] // 2 + 12])
                    self.save_ppm_progress_bar.set_pos([self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 - 112, self.WINDOW_SIZE[1] // 2 + 12])
                    self.save_ppm_progress_label.set_center([self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2])

                    thread = threading.Thread(target=lambda: self.render_animation(path, width, height))
                    thread.start()

        # animation is rendering
        elif self.save_ppm_render and self.save_ppm_save_button.is_pressed(event.x, event.y) and 350 <= event.y - self.WINDOW_SIZE[1] // 2 + 200:
            self.save_ppm_render = False

    def load_model(self, model):
        self.model.load_model(model)
        self.generate_image(set_as_vis=True)

    def render_animation(self, path: str, width: int, height: int):
        # render images
        images = []
        for frame in range(self.save_ppm_start_frame, self.save_ppm_end_frame + 1):
            if self.save_ppm_render:
                self.set_time_step(frame)
                image = resize(self.images[str(self.latent_space.squeeze().tolist())], (height, width), order=0,
                               mode='constant', anti_aliasing=False)
                image = image.astype(np.uint8)

                images.append(image)

                self.save_ppm_render_progress = (frame - self.save_ppm_start_frame) / (self.save_ppm_end_frame - self.save_ppm_start_frame)
                self.save_ppm_progress_bar.set_pos([self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 - 112 + 238 * self.save_ppm_render_progress, self.WINDOW_SIZE[1] // 2 + 12])
                self.save_ppm_progress_label.set_text(f"{frame - self.save_ppm_start_frame} / {(self.save_ppm_end_frame - self.save_ppm_start_frame)}")

        if self.save_ppm_render:
            # video parameters
            fps = 90
            frame_size = (width, height)

            # create video
            fourcc = cv2.VideoWriter_fourcc(*'XVID')

            # Create a VideoWriter object to write the video
            out = cv2.VideoWriter(path, fourcc, fps, frame_size)

            # Write each frame to the video file
            for frame in images:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)

            # Release the VideoWriter object and close the output video file
            out.release()

        self.close_save_popup()

    def close_save_popup(self):
        self.reset_ppm_entrys()

        self.save_ppm_save_button.set_color([73, 182, 91])
        self.save_ppm_save_label.set_text("Save")

        self.save_ppm_width_label.set_text("66")
        self.save_ppm_height_label.set_text("128")

        self.save_ppm_name_underline.set_color([200, 200, 200])
        self.save_ppm_dir_underline.set_color([200, 200, 200])
        self.save_ppm_size_underline_1.set_color([200, 200, 200])
        self.save_ppm_size_underline_2.set_color([200, 200, 200])
        self.save_ppm_frame_underline_1.set_color([200, 200, 200])
        self.save_ppm_frame_underline_2.set_color([200, 200, 200])

        self.save_ppm_back.delete()
        self.save_ppm_title.delete()
        self.save_ppm_exit_cross_l1.delete()
        self.save_ppm_exit_cross_l2.delete()
        self.save_ppm_name_label.delete()
        self.save_ppm_name_underline.delete()
        self.save_ppm_name_text.delete()
        self.save_ppm_dir_label.delete()
        self.save_ppm_dir_folder.delete()
        self.save_ppm_dir_underline.delete()
        self.save_ppm_dir_text.delete()
        self.save_ppm_size_label.delete()
        self.save_ppm_size_underline_1.delete()
        self.save_ppm_size_underline_2.delete()
        self.save_ppm_size_divider.delete()
        self.save_ppm_width_label.delete()
        self.save_ppm_height_label.delete()
        self.save_ppm_save_button.delete()
        self.save_ppm_save_button_cover.delete()
        self.save_ppm_save_label.delete()
        self.save_ppm_frame_label.delete()
        self.save_ppm_frame_underline_1.delete()
        self.save_ppm_frame_underline_2.delete()
        self.save_ppm_frame_divider.delete()
        self.save_ppm_sframe_label.delete()
        self.save_ppm_eframe_label.delete()
        self.save_ppm_progress_back.delete()
        self.save_ppm_progress_bar.delete()
        self.save_ppm_progress_label.delete()

        self.save_ppm = False

    def open_save_ppm(self):
        if not (key := str(self.latent_space.squeeze().tolist())) in self.images:
            self.generate_image(set_as_vis=False)

        self.save_ppm = True

        # define path and image name
        if self.save_ppm_mode == "Image":
            self.save_ppm_path = "Playground Images and Videos"
            num = 1
            self.save_ppm_img_name = f"Image {num}"
            while os.path.isfile(os.path.join(self.save_ppm_path, self.save_ppm_img_name + ".png")) is True:
                num += 1
                self.save_ppm_img_name = f"Image {num}"

            # set text to image
            self.save_ppm_title.set_text("Save Image")
            self.save_ppm_name_label.set_text("Image name:")
        # define path and video name
        else:
            self.save_ppm_path = "Playground Images and Videos"
            num = 1
            self.save_ppm_img_name = f"Video {num}"
            while os.path.isfile(os.path.join(self.save_ppm_path, self.save_ppm_img_name + ".avi")) is True:
                num += 1
                self.save_ppm_img_name = f"Video {num}"

            # set text to video
            self.save_ppm_title.set_text("Save Video")
            self.save_ppm_name_label.set_text("Video name:")
            self.save_ppm_eframe_label.set_text(f"{self.max_time_steps}")
            self.save_ppm_end_frame = self.max_time_steps

        self.save_ppm_name_text.set_text(self.save_ppm_img_name)
        self.set_ppm_pos()

        self.save_ppm_back.draw()
        self.save_ppm_title.draw()
        self.save_ppm_exit_cross_l1.draw()
        self.save_ppm_exit_cross_l2.draw()
        self.save_ppm_name_label.draw()
        self.save_ppm_name_underline.draw()
        self.save_ppm_name_text.draw()
        self.save_ppm_dir_label.draw()
        self.save_ppm_dir_folder.draw()
        self.save_ppm_dir_underline.draw()
        self.save_ppm_dir_text.draw()
        self.save_ppm_size_label.draw()
        self.save_ppm_size_underline_1.draw()
        self.save_ppm_size_underline_2.draw()
        self.save_ppm_size_divider.draw()
        self.save_ppm_width_label.draw()
        self.save_ppm_height_label.draw()
        self.save_ppm_save_button.draw()
        self.save_ppm_save_button_cover.draw()
        self.save_ppm_save_label.draw()
        if self.save_ppm_mode == "Video":
            self.save_ppm_frame_label.draw()
            self.save_ppm_frame_underline_1.draw()
            self.save_ppm_frame_underline_2.draw()
            self.save_ppm_frame_divider.draw()
            self.save_ppm_sframe_label.draw()
            self.save_ppm_eframe_label.draw()

    def reset_ppm_entrys(self):
        error_in_input = False
        
        if self.save_ppm:
            # name
            if self.save_ppm_name_entry.winfo_ismapped():
                self.save_ppm_img_name = self.save_ppm_name_entry.get()

                # shorten string for visualisation
                if self.save_ppm_name_text.font.measure(text := self.save_ppm_name_entry.get()) > 250:
                    for i in range(len(text)):
                        if self.save_ppm_name_text.font.measure(text[:i] + "...") > 250:
                            text = text[:i - 1] + "..."
                            break

                # set new string
                self.save_ppm_name_text.set_text(text)
                self.save_ppm_name_entry.delete(0, tk.END)
                self.save_ppm_name_entry.place_forget()

                # update underline color to indicate error
                file_path = os.path.join(self.save_ppm_path, self.save_ppm_img_name + ".png")
                if os.path.exists(self.save_ppm_path) and os.path.isdir(self.save_ppm_path) and os.path.isfile(file_path):
                    self.save_ppm_name_underline.set_color([215, 64, 64])
                    error_in_input = True
                else:
                    self.save_ppm_name_underline.set_color([200, 200, 200])
            # dir
            elif self.save_ppm_dir_entry.winfo_ismapped():
                self.save_ppm_path = self.save_ppm_dir_entry.get()

                # shorten string for visualisation
                if self.save_ppm_dir_text.font.measure(text := self.save_ppm_dir_entry.get()) > 225:
                    for i in range(len(text)):
                        if self.save_ppm_dir_text.font.measure(text[:i] + "...") > 225:
                            text = text[:i - 1] + "..."
                            break

                # set new string
                self.save_ppm_dir_text.set_text(text)
                self.save_ppm_dir_entry.delete(0, tk.END)
                self.save_ppm_dir_entry.place_forget()

                # update underline color to indicate error
                if os.path.exists(self.save_ppm_path) and os.path.isdir(self.save_ppm_path):
                    self.save_ppm_dir_underline.set_color([200, 200, 200])

                    # update name underline color
                    file_path = os.path.join(self.save_ppm_path, self.save_ppm_img_name + ".png")
                    if os.path.isfile(file_path):
                        self.save_ppm_name_underline.set_color([215, 64, 64])
                        error_in_input = True
                    else:
                        self.save_ppm_name_underline.set_color([200, 200, 200])
                else:
                    self.save_ppm_dir_underline.set_color([215, 64, 64])
                    self.save_ppm_name_underline.set_color([200, 200, 200])
                    error_in_input = True
            # width
            elif self.save_ppm_width_entry.winfo_ismapped():
                self.save_ppm_width_label.set_text(self.save_ppm_width_entry.get())
                self.save_ppm_width_entry.delete(0, tk.END)
                self.save_ppm_width_entry.place_forget()

                # update underline color to indicate error
                try:
                    int(self.save_ppm_width_label.text)
                    self.save_ppm_size_underline_1.set_color([200, 200, 200])
                except:
                    self.save_ppm_size_underline_1.set_color([215, 64, 64])
                    error_in_input = True
            # height
            elif self.save_ppm_height_entry.winfo_ismapped():
                self.save_ppm_height_label.set_text(self.save_ppm_height_entry.get())
                self.save_ppm_height_entry.delete(0, tk.END)
                self.save_ppm_height_entry.place_forget()

                # update underline color to indicate error
                try:
                    int(self.save_ppm_height_label.text)
                    self.save_ppm_size_underline_2.set_color([200, 200, 200])
                except:
                    self.save_ppm_size_underline_2.set_color([215, 64, 64])
                    error_in_input = True

            # start frame
            elif self.save_ppm_sframe_entry.winfo_ismapped():
                self.save_ppm_sframe_label.set_text(self.save_ppm_sframe_entry.get())
                self.save_ppm_sframe_entry.delete(0, tk.END)
                self.save_ppm_sframe_entry.place_forget()

                try:
                    self.save_ppm_start_frame = int(self.save_ppm_sframe_label.text)
                    if self.save_ppm_end_frame > self.save_ppm_start_frame:
                        self.save_ppm_frame_underline_1.set_color([200, 200, 200])
                    else:
                        self.save_ppm_frame_underline_1.set_color([215, 64, 64])
                        error_in_input = True
                except:
                    self.save_ppm_frame_underline_1.set_color([215, 64, 64])
                    error_in_input = True

            # end frame
            elif self.save_ppm_eframe_entry.winfo_ismapped():
                self.save_ppm_eframe_label.set_text(self.save_ppm_eframe_entry.get())
                self.save_ppm_eframe_entry.delete(0, tk.END)
                self.save_ppm_eframe_entry.place_forget()

                try:
                    self.save_ppm_end_frame = int(self.save_ppm_eframe_label.text)
                    if self.save_ppm_end_frame <= self.max_time_steps:
                        self.save_ppm_frame_underline_2.set_color([200, 200, 200])
                    else:
                        self.save_ppm_frame_underline_2.set_color([215, 64, 64])
                        error_in_input = True

                    if self.save_ppm_end_frame > self.save_ppm_start_frame:
                        self.save_ppm_frame_underline_1.set_color([200, 200, 200])
                    else:
                        self.save_ppm_frame_underline_1.set_color([215, 64, 64])
                        error_in_input = True
                except:
                    self.save_ppm_frame_underline_2.set_color([215, 64, 64])
                    error_in_input = True

            # change save button appearance
            if error_in_input or self.save_ppm_name_underline.color == [215, 64, 64] or self.save_ppm_dir_underline.color == [215, 64, 64] \
                    or self.save_ppm_size_underline_1.color == [215, 64, 64] or self.save_ppm_size_underline_2.color == [215, 64, 64] \
                    or self.save_ppm_frame_underline_1.color == [215, 64, 64] or self.save_ppm_frame_underline_2.color == [215, 64, 64]:
                self.save_ppm_save_button.set_color([200, 200, 200])
            else:
                self.save_ppm_save_button.set_color([73, 182, 91])

    def set_ppm_pos(self):
        if self.save_ppm:
            self.save_ppm_back.set_pos([self.WINDOW_SIZE[0] // 2 - 150, self.WINDOW_SIZE[1] // 2 - 200], [self.WINDOW_SIZE[0] // 2 + 150, self.WINDOW_SIZE[1] // 2 + 200])
            self.save_ppm_title.set_center([self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 175])
            if not self.save_ppm_render:
                self.save_ppm_exit_cross_l1.set_pos([self.WINDOW_SIZE[0] // 2 + 118, self.WINDOW_SIZE[1] // 2 - 168], [self.WINDOW_SIZE[0] // 2 + 133, self.WINDOW_SIZE[1] // 2 - 183])
                self.save_ppm_exit_cross_l2.set_pos([self.WINDOW_SIZE[0] // 2 + 118, self.WINDOW_SIZE[1] // 2 - 182], [self.WINDOW_SIZE[0] // 2 + 133, self.WINDOW_SIZE[1] // 2 - 167])
                center = [self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2 if self.save_ppm_mode == "Image" else self.WINDOW_SIZE[1] // 2 - 33]
                self.save_ppm_name_label.set_center([center[0] - 125, center[1] - 92])
                self.save_ppm_name_underline.set_pos([center[0] - 125, center[1] - 47], [center[0] + 125, center[1] - 47])
                self.save_ppm_name_text.set_center([center[0] - 125, center[1] - 48])
                self.save_ppm_dir_label.set_center([center[0] - 125, center[1] - 27])
                self.save_ppm_dir_folder.set_center([center[0] + 115, center[1] + 8])
                self.save_ppm_dir_underline.set_pos([center[0] - 125, center[1] + 18], [center[0] + 100, center[1] + 18])
                self.save_ppm_dir_text.set_center([center[0] - 125, center[1] + 17])
                self.save_ppm_size_label.set_center([center[0] - 125, center[1] + 38])
                self.save_ppm_size_underline_1.set_pos([center[0] - 125, center[1] + 83], [center[0] - 10, center[1] + 83])
                self.save_ppm_size_underline_2.set_pos([center[0] + 125, center[1] + 83], [center[0] + 10, center[1] + 83])
                self.save_ppm_size_divider.set_center([center[0], center[1] + 82])
                self.save_ppm_width_label.set_center([center[0] - 125, center[1] + 82])
                self.save_ppm_height_label.set_center([center[0] + 10, center[1] + 82])
                if self.save_ppm_mode == "Video":
                    self.save_ppm_frame_label.set_center([center[0] - 125, center[1] + 103])
                    self.save_ppm_frame_underline_1.set_pos([center[0] - 125, center[1] + 148], [center[0] - 10, center[1] + 148])
                    self.save_ppm_frame_underline_2.set_pos([center[0] + 125, center[1] + 148], [center[0] + 10, center[1] + 148])
                    self.save_ppm_frame_divider.set_center([center[0], center[1] + 147])
                    self.save_ppm_sframe_label.set_center([center[0] - 125, center[1] + 147])
                    self.save_ppm_eframe_label.set_center([center[0] + 10, center[1] + 147])
            else:
                self.save_ppm_progress_back.set_pos([self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 + 125, self.WINDOW_SIZE[1] // 2 + 12])
                self.save_ppm_progress_bar.set_pos([self.WINDOW_SIZE[0] // 2 - 125, self.WINDOW_SIZE[1] // 2 - 12], [self.WINDOW_SIZE[0] // 2 - 112 + 238 * self.save_ppm_render_progress, self.WINDOW_SIZE[1] // 2 + 12])
                self.save_ppm_progress_label.set_center([self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2])
            self.save_ppm_save_button.set_pos([self.WINDOW_SIZE[0] // 2 - 150, self.WINDOW_SIZE[1] // 2 + 140], [self.WINDOW_SIZE[0] // 2 + 150, self.WINDOW_SIZE[1] // 2 + 200])
            self.save_ppm_save_button_cover.set_pos([self.WINDOW_SIZE[0] // 2 - 150, self.WINDOW_SIZE[1] // 2 + 140], [self.WINDOW_SIZE[0] // 2 + 150, self.WINDOW_SIZE[1] // 2 + 150])
            self.save_ppm_save_label.set_center([self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2 + 175])

            # entrys
            if self.save_ppm_name_entry.winfo_ismapped():
                self.save_ppm_name_entry.place(x=center[0] - 128, y=center[1] - 66, width=250)
            if self.save_ppm_dir_entry.winfo_ismapped():
                self.save_ppm_dir_entry.place(x=center[0] - 128, y=center[1] - 1, width=225)
            if self.save_ppm_width_entry.winfo_ismapped():
                self.save_ppm_width_entry.place(x=center[0] - 128, y=center[1] + 64, width=115)
            if self.save_ppm_height_entry.winfo_ismapped():
                self.save_ppm_height_entry.place(x=center[0] + 7, y=center[1] + 64, width=115)
            if self.save_ppm_sframe_entry.winfo_ismapped():
                self.save_ppm_sframe_entry.place(x=center[0] - 128, y=center[1] + 129, width=115)
            if self.save_ppm_eframe_entry.winfo_ismapped():
                self.save_ppm_eframe_entry.place(x=center[0] + 7, y=center[1] + 129, width=115)

    def button_1_motion(self, event):
        # slider point has been pressed
        if self.slider_pressed is not None:
            if 28 <= event.x <= 292:
                # update parameters
                self.latent_sliders[self.slider_pressed[1]][5].set_center([event.x, 133 + 92 * self.slider_pressed[0] + self.y_scroll])
                self.latent_space[0, int(self.slider_pressed[1]), 0, 0] = (event.x - 160) / 132

                # update latent space visualisation
                self.visualise_latent()

            else:
                # update parameters
                self.latent_sliders[self.slider_pressed[1]][5].set_center([28 if event.x < 28 else 292, 133 + 92 * self.slider_pressed[0] + self.y_scroll])
                self.latent_space[0, int(self.slider_pressed[1]), 0, 0] = -1 if event.x < 28 else 1

                # update latent space visualisation
                self.visualise_latent()

        # move timestep
        if self.time_line_pressed:
            self.current_time_step = round((event.y - 50) / (self.WINDOW_SIZE[1] - 100) * self.max_time_steps)
            self.current_time_step = 0 if self.current_time_step < 0 else self.max_time_steps if self.current_time_step > self.max_time_steps else self.current_time_step

            self.set_time_step(self.current_time_step)

    def button_1_release(self, event):
        # point was selected
        if self.slider_pressed is not None:
            self.slider_pressed = None

            # update image
            if self.auto_gen and self.model_loaded:
                thread = threading.Thread(target=lambda: self.generate_image(set_as_vis=True))
                thread.start()

        # timestep was moved
        if self.time_line_pressed:
            self.time_line_pressed = False

    def delete_slider(self, key, menu_open: bool):
        # remove from screen
        self.latent_sliders[key][0].delete()
        self.latent_sliders[key][1].delete()
        self.latent_sliders[key][2].delete()
        self.latent_sliders[key][3].delete()
        self.latent_sliders[key][4].delete()
        self.latent_sliders[key][5].delete()
        self.latent_sliders[key][6].delete()
        self.latent_sliders[key][7].delete()
        # remove from dict
        self.latent_sliders.pop(key)
        # reset scroll
        if len(list(self.latent_sliders)) * 92 + 90 < self.WINDOW_SIZE[1]:
            self.y_scroll = 0
        elif len(list(self.latent_sliders)) * 92 + 90 + self.y_scroll < self.WINDOW_SIZE[1]:
            self.y_scroll = self.WINDOW_SIZE[1] - (len(list(self.latent_sliders)) * 92 + 95)
        # update rest
        self.new_slider_pos -= 1
        self.update_slider_pos([10 if menu_open else -320, 75])

    # mouse wheel
    def mouse_wheel(self, event):
        if self.latent_menu and event.x <= 320 and len(list(self.latent_sliders)) * 92 + 90 > self.WINDOW_SIZE[1]:
            scroll_length = round(abs(event.delta / 8))
            if event.delta > 0 and self.y_scroll + scroll_length <= 0:
                self.y_scroll += scroll_length
            elif event.delta > 0 and self.y_scroll + scroll_length > 0:
                self.y_scroll = 0
            elif event.delta < 0 and len(list(self.latent_sliders)) * 92 + 130 - self.WINDOW_SIZE[1] + self.y_scroll - scroll_length > 0:
                self.y_scroll -= scroll_length
            elif event.delta > 0:
                self.y_scroll = self.WINDOW_SIZE[1] - (len(list(self.latent_sliders)) * 92 + 95)

            # update indication label
            if self.edit_slider:
                text_length = Font(family="Arial", size=-25).measure(self.edit_slider_key[0])
                self.edit_indication_line.set_pos(
                    [160 + text_length / 2, 81 + 92 * self.edit_slider_key[1] + self.y_scroll],
                    [160 + text_length / 2, 105 + 92 * self.edit_slider_key[1] + self.y_scroll])

            self.update_slider_pos([10, 75])

    # key event
    def key(self, event):
        if ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].count(event.char):
            # update label
            if self.edit_slider:
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + event.char)))
            # update time step
            elif self.time_step_selected and (num := int(self.time_step_label.text + event.char)) <= self.max_time_steps:
                self.current_time_step = num

                # update indication line
                x = self.time_step_label.font.measure(f"{self.current_time_step}") / 2 + self.WINDOW_SIZE[0] - 25
                self.edit_time_line.set_pos([x, self.WINDOW_SIZE[1] - 39], [x, self.WINDOW_SIZE[1] - 26])

                self.set_time_step(self.current_time_step, animation=True, animation_time=0.2)
            # update max time steps
            elif self.max_time_steps_selected and (num := int(self.max_time_step_label.text + event.char)) <= 999999:
                self.max_time_step_label.set_text(str(num))
                self.max_time_steps = num

                # update indication line
                x = self.max_time_step_label.font.measure(self.max_time_step_label.text) / 2 + self.WINDOW_SIZE[0] - 25
                self.edit_time_line.set_pos([x, self.WINDOW_SIZE[1] - 23], [x, self.WINDOW_SIZE[1] - 11])

                self.set_time_step(self.current_time_step, animation=True, animation_time=0.2)

                # reset keyframes
                for ind in self.key_frame_indicator:
                    ind[3].delete()

                self.key_frame_indicator.clear()

        elif event.keysym == 'BackSpace':
            # update label
            if self.edit_slider and len(self.latent_sliders[self.edit_slider_key[0]][3].text) >= 1:
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(self.latent_sliders[self.edit_slider_key[0]][3].text[:-1])
            # update time step
            elif self.time_step_selected and len(self.time_step_label.text) >= 1:
                self.current_time_step = int(self.time_step_label.text[:-1]) if len(self.time_step_label.text[:-1]) > 0 else 0

                # update indication line
                x = self.time_step_label.font.measure(f"{self.current_time_step}") / 2 + self.WINDOW_SIZE[0] - 25
                self.edit_time_line.set_pos([x, self.WINDOW_SIZE[1] - 39], [x, self.WINDOW_SIZE[1] - 26])

                self.set_time_step(self.current_time_step, animation=True, animation_time=0.2)
            # update max time steps
            elif self.max_time_steps_selected and len(self.max_time_step_label.text) >= 1:
                self.max_time_step_label.set_text(self.max_time_step_label.text[:-1] if len(self.max_time_step_label.text[:-1]) > 0 else "0")
                self.max_time_steps = int(self.max_time_step_label.text) if self.max_time_step_label.text != "0" else 1

                # update current time step
                if self.current_time_step > int(self.max_time_step_label.text):
                    self.current_time_step = int(self.max_time_step_label.text)

                # update indication line
                x = self.max_time_step_label.font.measure(self.max_time_step_label.text) / 2 + self.WINDOW_SIZE[0] - 25
                self.edit_time_line.set_pos([x, self.WINDOW_SIZE[1] - 23], [x, self.WINDOW_SIZE[1] - 11])

                self.set_time_step(self.current_time_step, animation=True, animation_time=0.2)

                # reset keyframes
                for ind in self.key_frame_indicator:
                    ind[3].delete()

                self.key_frame_indicator.clear()

        if event.keysym == 'Return':
            # set new slider parameters
            if self.edit_slider:
                if (self.latent_sliders[self.edit_slider_key[0]][3].text in self.latent_sliders and self.edit_slider_key[0] != self.latent_sliders[self.edit_slider_key[0]][3].text) or \
                   (len(self.latent_sliders[self.edit_slider_key[0]][3].text) >= 1 and int(self.latent_sliders[self.edit_slider_key[0]][3].text) >= 100) or \
                   self.latent_sliders[self.edit_slider_key[0]][3].text == '':
                    self.latent_sliders[self.edit_slider_key[0]][1].set_color([255, 150, 150], animation=True, animation_time=0.2)
                    self.latent_sliders[self.edit_slider_key[0]][1].set_color([215, 64, 64], animation=True, animation_time=0.2)
                else:
                    # update dict
                    new_dict = {}
                    new_key = self.latent_sliders[self.edit_slider_key[0]][3].text
                    # loop over each key
                    for key, value in self.latent_sliders.items():
                        if key == self.edit_slider_key[0]:
                            new_dict[new_key] = value
                        else:
                            new_dict[key] = value
                    # update dict
                    self.latent_sliders.clear()
                    self.latent_sliders.update(new_dict)

                    # change visuals
                    self.edit_indication_line.delete()
                    top_left = [10, 75 + 92 * self.edit_slider_key[1] + self.y_scroll]
                    value = 150 + self.latent_space.tolist()[0][int(new_key)][0][0] * 132
                    self.latent_sliders[new_key][5].set_center([top_left[0] + value, top_left[1] + 58], animation=True, animation_time=0.2)

                    # terminate edit
                    self.edit_slider = False
                    self.edit_slider_key = None

            # set new timeline parameters
            if self.time_step_selected or self.max_time_steps_selected:
                # reset parameters
                self.time_step_selected = False
                self.max_time_steps_selected = False

                # delete indication line
                self.edit_time_line.delete()

            self.reset_ppm_entrys()

        elif event.keysym == "Escape":
            # reset sliders
            if self.edit_slider:
                self.reset_slider()
            # reset animation menu
            if self.time_step_selected or self.max_time_steps_selected:
                self.reset_animation_entries()

        else:
            if self.edit_slider:
                # update indicator
                text_length = Font(family="Arial", size=-25).measure(self.latent_sliders[self.edit_slider_key[0]][3].text)
                self.edit_indication_line.set_pos(
                    [160 + text_length / 2, 81 + 92 * self.edit_slider_key[1] + self.y_scroll],
                    [160 + text_length / 2, 105 + 92 * self.edit_slider_key[1] + self.y_scroll])
                # check if valid
                if (self.latent_sliders[self.edit_slider_key[0]][3].text in self.latent_sliders and self.edit_slider_key[0] != self.latent_sliders[self.edit_slider_key[0]][3].text) or \
                   (len(self.latent_sliders[self.edit_slider_key[0]][3].text) >= 1 and int(self.latent_sliders[self.edit_slider_key[0]][3].text) >= 100) or \
                   self.latent_sliders[self.edit_slider_key[0]][3].text == '':
                    self.latent_sliders[self.edit_slider_key[0]][1].set_color([215, 64, 64], animation=True, animation_time=0.2)
                elif self.latent_sliders[self.edit_slider_key[0]][1].color != [205, 205, 205]:
                    self.latent_sliders[self.edit_slider_key[0]][1].set_color([205, 205, 205], animation=True, animation_time=0.2)

        # set keyframe
        if event.char == "i" or event.char == "I":
            # keyframe the whole latent space
            if -200 <= event.x - self.WINDOW_SIZE[0] // 2 <= 200 and self.WINDOW_SIZE[1] - event.y <= 50:
                # shift
                if event.state & 1:
                    self.remove_keyframe([i for i in range(100)])
                # no shift
                else:
                    self.add_keyframe([i for i in range(100)], self.latent_space.squeeze().tolist())
            # keyframe a single slider
            elif event.x <= 320 and len(self.latent_sliders.keys()) > (index := floor((event.y - 75 - self.y_scroll) / 92)):
                indexes = [int(list(self.latent_sliders.keys())[index])]
                values = [self.latent_space.squeeze().tolist()[indexes[0]]]

                # shift
                if event.state & 1:
                    self.remove_keyframe(indexes)
                # no shift
                else:
                    self.add_keyframe(indexes, values)

    # generate image from model and save it
    def generate_image(self, set_as_vis: bool = False):
        if not (key := str(self.latent_space.squeeze().tolist())) in self.images:
            # generate image using model
            array = self.model.generate_image(self.latent_space)
            # convert to rgb image
            image = self.decode_data(array.detach()).astype(np.uint8)
            image = image[0].reshape(128, 66)
            image = self.visualiser.visualise(image)
            # convert prob image
            prob = self.decode_data(array.detach(), probability=True)[0]
            prob = (prob - prob.min()) / (prob.max() - prob.min())
            prob = np.array([220, 220, 220]) - prob * np.array([93, 16, 80])
            # add image to dict
            self.images.update({key: image})
            self.images_prob.update({key: prob})

            # visualise the image
            if set_as_vis:
                self.image_key = key

                self.visualise_generated_image()
        else:
            self.image_key = str(self.latent_space.squeeze().tolist())
            self.visualise_generated_image()

    # add keyframe
    def add_keyframe(self, indexes: list[int], values: list[float]):
        # change keyframe
        if [val[0] for val in self.key_frame_indicator].count(self.current_time_step):
            key_frame_index = [val[0] for val in self.key_frame_indicator].index(self.current_time_step)
            for index, val in zip(indexes, values):
                # existing index
                if self.key_frame_indicator[key_frame_index][1].count(index):
                    self.key_frame_indicator[key_frame_index][2][self.key_frame_indicator[key_frame_index][1].index(index)] = val
                # new index
                else:
                    self.key_frame_indicator[key_frame_index][1].append(index)
                    self.key_frame_indicator[key_frame_index][2].append(val)
        # set new keyframe
        else:
            rect = Circle(self.canvas, [self.WINDOW_SIZE[0] - 15, (self.WINDOW_SIZE[1] - 100) / self.max_time_steps * self.current_time_step + 50], 3, [73, 182, 91], 0, [0, 0, 0])
            rect.draw()
            self.key_frame_indicator.append([self.current_time_step, indexes, values, rect])

        self.calculate_animation_functions()

    def remove_keyframe(self, indexes: list[int]):
        # remove keyframe
        if [val[0] for val in self.key_frame_indicator].count(self.current_time_step):
            key_frame_index = [val[0] for val in self.key_frame_indicator].index(self.current_time_step)
            for index in indexes:
                if self.key_frame_indicator[key_frame_index][1].count(index):
                    pos = self.key_frame_indicator[key_frame_index][1].index(index)

                    # remove values
                    self.key_frame_indicator[key_frame_index][1].pop(pos)
                    self.key_frame_indicator[key_frame_index][2].pop(pos)

                    # remove keyframe from list
                    if len(self.key_frame_indicator[key_frame_index][1]) == 0:
                        self.key_frame_indicator[key_frame_index][3].delete()

                        self.key_frame_indicator.pop(key_frame_index)
                        break

        self.calculate_animation_functions()

    # visualise image
    def visualise_generated_image(self):
        # probability image
        if self.probability and self.image_key != "Placeholder":
            # load image
            image = self.images_prob[self.image_key]
            # resize image
            image = resize(image, ((self.WINDOW_SIZE[1] - 150), round(66 * ((self.WINDOW_SIZE[1] - 150) / 128))),
                           order=0, mode='constant', anti_aliasing=False)
        # normal image
        else:
            # load image
            image = self.images[self.image_key]
            # resize image
            image = resize(image, ((self.WINDOW_SIZE[1] - 150), round(66 * ((self.WINDOW_SIZE[1] - 150) / 128))),
                           order=0, mode='constant', anti_aliasing=False)
        # add image to screen
        self.generated_image.set_image(pil.ImageTk.PhotoImage(pil.Image.fromarray(np.uint8(image))))

    # resize window
    def resize(self, event):
        # resize canvas / update class parameter
        self.canvas.configure(width=event.width, height=event.height)
        self.WINDOW_SIZE = [event.width, event.height]

        # reset scroll
        if len(list(self.latent_sliders)) * 92 + 90 < self.WINDOW_SIZE[1]:
            self.y_scroll = 0
        elif len(list(self.latent_sliders)) * 92 + 90 + self.y_scroll < self.WINDOW_SIZE[1]:
            self.y_scroll = self.WINDOW_SIZE[1] - (len(list(self.latent_sliders)) * 92 + 95)

        self.update_slider_pos([10 if self.latent_menu else -320, 75])

        # resize model selection
        if self.model_loaded:
            self.model_sel_back.set_pos([self.WINDOW_SIZE[0] // 2 - 255, 10], [self.WINDOW_SIZE[0] // 2 + 85, 60])
            self.model_sel_model_label.set_center([self.WINDOW_SIZE[0] // 2 - 235, 46])
            self.model_sel_gener_label.set_center([self.WINDOW_SIZE[0] // 2 - 235, 30])
            self.model_sel_folder_back.set_pos([self.WINDOW_SIZE[0] // 2 + 95, 10],
                                               [self.WINDOW_SIZE[0] // 2 + 145, 60])
            self.image_save_back.set_pos([self.WINDOW_SIZE[0] // 2 + 155, 10],
                                         [self.WINDOW_SIZE[0] // 2 + 255, 60])
            self.model_sel_folder_img.set_center([self.WINDOW_SIZE[0] // 2 + 120, 35])
            self.save_image_img.set_center([self.WINDOW_SIZE[0] // 2 + 180, 35])
            self.save_video_img.set_center([self.WINDOW_SIZE[0] // 2 + 230, 35])
        else:
            self.model_sel_back.set_pos([self.WINDOW_SIZE[0] // 2 - 255, 10], [self.WINDOW_SIZE[0] // 2 + 255, 60])
            self.model_sel_model_label.set_center([self.WINDOW_SIZE[0] // 2 - 235, 35])
            self.model_sel_gener_label.set_center([self.WINDOW_SIZE[0] // 2 - 235, 30])
            self.model_sel_folder_back.set_pos([self.WINDOW_SIZE[0] // 2 + 95, 10],
                                               [self.WINDOW_SIZE[0] // 2 + 145, 60])
            self.image_save_back.set_pos([self.WINDOW_SIZE[0] // 2 + 155, 10],
                                         [self.WINDOW_SIZE[0] // 2 + 255, 60])
            self.model_sel_folder_img.set_center([self.WINDOW_SIZE[0] // 2 + 120, 35])
            self.save_image_img.set_center([self.WINDOW_SIZE[0] // 2 + 180, 35])
            self.save_video_img.set_center([self.WINDOW_SIZE[0] // 2 + 230, 35])

        # resize animation menu
        self.time_step_line.set_pos([self.WINDOW_SIZE[0] - 25, 50], [self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 50])
        self.time_step_indication.set_center([self.WINDOW_SIZE[0] - 25, (self.WINDOW_SIZE[1] - 100) / self.max_time_steps * self.current_time_step + 50])
        self.time_step_label.set_center([self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 33])
        self.max_time_step_label.set_center([self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 17])

        if self.run_time:
            self.time_play_button_1.set_points(
                [[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 27, 18], [self.WINDOW_SIZE[0] - 27, 32],
                 [self.WINDOW_SIZE[0] - 31, 32]])
            self.time_play_button_2.set_points(
                [[self.WINDOW_SIZE[0] - 23, 18], [self.WINDOW_SIZE[0] - 19, 18], [self.WINDOW_SIZE[0] - 19, 32],
                 [self.WINDOW_SIZE[0] - 23, 32]])
        else:
            self.time_play_button_1.set_points(
                [[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]])
            self.time_play_button_2.set_points(
                [[self.WINDOW_SIZE[0] - 31, 18], [self.WINDOW_SIZE[0] - 19, 25], [self.WINDOW_SIZE[0] - 31, 32]])

        # resize generated image
        self.generated_image.set_center([self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2])
        self.visualise_generated_image()

        # resize keyframes
        for key in self.key_frame_indicator:
            index = key[0]
            key[3].set_center([self.WINDOW_SIZE[0] - 15, (self.WINDOW_SIZE[1] - 100) / self.max_time_steps * index + 50])

        self.set_ppm_pos()

        # latent space
        self.visualise_latent()

    # update slider position
    def update_slider_pos(self, top_left: [float, float], animation: bool = False, animation_time: float = None):
        origin = copy.copy(top_left)
        for i, key in enumerate(self.latent_sliders.keys()):
            # calculate positions
            index = int(key)
            top_left = [origin[0], origin[1] + 92 * i + self.y_scroll]
            value = self.latent_space.tolist()[0][index][0][0]
            # animate sliders
            self.latent_sliders[key][0].set_pos([top_left[0], top_left[1]], [top_left[0] + 300, top_left[1] + 82],
                                                animation=animation, animation_time=animation_time)
            self.latent_sliders[key][1].set_pos([top_left[0], top_left[1]], [top_left[0] + 300, top_left[1] + 46],
                                                animation=animation, animation_time=animation_time)
            self.latent_sliders[key][2].set_pos([top_left[0], top_left[1] + 36], [top_left[0] + 300, top_left[1] + 46],
                                                animation=animation, animation_time=animation_time)
            self.latent_sliders[key][3].set_center([top_left[0] + 150, top_left[1] + 18], animation=animation,
                                                   animation_time=animation_time)
            self.latent_sliders[key][4].set_pos([top_left[0] + 18, top_left[1] + 58],
                                                [top_left[0] + 282, top_left[1] + 59], animation=animation,
                                                animation_time=animation_time)
            self.latent_sliders[key][5].set_center([top_left[0] + 150 + value * 132, top_left[1] + 58],
                                                   animation=animation, animation_time=animation_time)
            self.latent_sliders[key][6].set_pos([top_left[0] + 277, top_left[1] + 13],
                                                [top_left[0] + 288, top_left[1] + 24], animation=animation,
                                                animation_time=animation_time)
            self.latent_sliders[key][7].set_pos([top_left[0] + 277, top_left[1] + 23],
                                                [top_left[0] + 288, top_left[1] + 12], animation=animation,
                                                animation_time=animation_time)

        self.new_slider_back.set_pos([origin[0], self.new_slider_pos * 92 + 75 + self.y_scroll],
                                     [origin[0] + 300, self.new_slider_pos * 92 + 115 + self.y_scroll],
                                     animation=animation, animation_time=animation_time)
        self.new_slider_label.set_center([origin[0] + 150, self.new_slider_pos * 92 + 95 + self.y_scroll],
                                         animation=animation, animation_time=animation_time)

        # probability toggle
        self.prob_label.set_center([origin[0] + 19, origin[1] - 17], animation=animation, animation_time=animation_time)
        self.prob_indi.set_pos([origin[0], origin[1] - 24], [origin[0] + 13, origin[1] - 11], animation=animation, animation_time=animation_time)
        # auto generate toggle
        self.auto_gen_label.set_center([origin[0] + 169, origin[1] - 17], animation=animation, animation_time=animation_time)
        self.auto_gen_indi.set_pos([origin[0] + 150, origin[1] - 24], [origin[0] + 163, origin[1] - 11], animation=animation, animation_time=animation_time)

    # new slider
    def create_new_slider(self):
        # define parameters
        new_index = min([i for i in range(100) if str(i) not in list(self.latent_sliders.keys())])
        top_left = [-320 if not self.latent_menu else 10, 75 + 92 * len(list(self.latent_sliders.keys())) + self.y_scroll]
        value = self.latent_space.tolist()[0][new_index][0][0]
        # create visual components
        background = Rectangle(self.canvas, [top_left[0], top_left[1]], [top_left[0] + 300, top_left[1] + 82], 10, [240, 240, 240], 0, [240, 240, 240])
        label_background = Rectangle(self.canvas, [top_left[0], top_left[1]], [top_left[0] + 300, top_left[1] + 46], 10, [205, 205, 205], 0, [240, 240, 240])
        background_cover = Rectangle(self.canvas, [top_left[0], top_left[1] + 36], [top_left[0] + 300, top_left[1] + 46], 0, [240, 240, 240], 0, [240, 240, 240])
        label = Text(self.canvas, f"{new_index}", [top_left[0] + 150, top_left[1] + 18], [50, 50, 50], 25)
        slider = Rectangle(self.canvas, [top_left[0] + 18, top_left[1] + 58], [top_left[0] + 282, top_left[1] + 59], 0, [205, 205, 205], 0, [240, 240, 240])
        slider_point = Circle(self.canvas, [top_left[0] + 150 + value * 132, top_left[1] + 58], 5, [73, 182, 91], 0, [0, 0, 0])
        slider_delete_1 = Line(self.canvas, [top_left[0] + 277, top_left[1] + 13], [top_left[0] + 288, top_left[1] + 24], [150, 150, 150], 1)
        slider_delete_2 = Line(self.canvas, [top_left[0] + 277, top_left[1] + 23], [top_left[0] + 288, top_left[1] + 12], [150, 150, 150], 1)
        # add slider to the dict
        self.latent_sliders.update({f"{new_index}": [background, label_background, background_cover, label, slider, slider_point, slider_delete_1, slider_delete_2]})
        # draw slider
        self.latent_sliders[f"{new_index}"][0].draw()
        self.latent_sliders[f"{new_index}"][1].draw()
        self.latent_sliders[f"{new_index}"][2].draw()
        self.latent_sliders[f"{new_index}"][3].draw()
        self.latent_sliders[f"{new_index}"][4].draw()
        self.latent_sliders[f"{new_index}"][5].draw()
        self.latent_sliders[f"{new_index}"][6].draw()
        self.latent_sliders[f"{new_index}"][7].draw()
        # update new slider pos
        self.new_slider_pos += 1
        self.new_slider_back.set_pos([top_left[0], self.new_slider_pos * 92 + 75 + self.y_scroll], [top_left[0] + 300, self.new_slider_pos * 92 + 115 + self.y_scroll])
        self.new_slider_label.set_center([top_left[0] + 150, self.new_slider_pos * 92 + 95 + self.y_scroll])
        # rise menu title
        if self.latent_label_back.object is not None:
            self.canvas.tag_raise(self.latent_label_back.object)
            self.canvas.tag_raise(self.latent_label.object)
            self.canvas.tag_raise(self.latent_toggle_back.object)
            self.canvas.tag_raise(self.latent_toggle_l1.object)
            self.canvas.tag_raise(self.latent_toggle_l2.object)
            self.canvas.tag_raise(self.prob_indi.object)
            self.canvas.tag_raise(self.prob_label.object)
            self.canvas.tag_raise(self.auto_gen_indi.object)
            self.canvas.tag_raise(self.auto_gen_label.object)

    # start
    def mainloop(self):
        self.root.mainloop()

    @staticmethod
    def decode_data(data, probability=False):
        # rearrange data and create new numpy array
        data = data.permute(0, 3, 2, 1)
        output_array = np.zeros((data.shape[0], data.shape[1], data.shape[2], 1))

        for img in range(data.shape[0]):
            # Convert the data tensor to a numpy array
            data_np = data[img].detach().numpy()
            value = np.max(data_np, axis=2) if probability else np.argmax(data_np, axis=2)
            value = value.reshape((data.shape[1], data.shape[2], 1))
            # convert active chanel to integer
            output_array[img] = value

        return output_array


class Generator(object):
    def __init__(self, latent_dim=100, num_feat_maps_gen=100, color_channels=13):
        self.generator = nn.Sequential(
            # (latent_dim, 1, 1)
            nn.ConvTranspose2d(latent_dim, num_feat_maps_gen * 16, kernel_size=12, stride=2, padding=4, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 16),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 16, 4, 4)
            nn.ConvTranspose2d(num_feat_maps_gen * 16, num_feat_maps_gen * 8, kernel_size=9, stride=2, padding=0,
                               bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 8, 15, 15)
            nn.ConvTranspose2d(num_feat_maps_gen * 8, num_feat_maps_gen * 8, kernel_size=7, stride=2, padding=2,
                               bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 8, 31, 31)
            nn.ConvTranspose2d(num_feat_maps_gen * 8, num_feat_maps_gen * 4, kernel_size=4, stride=(1, 2), padding=1,
                               bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 4),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 4, 32, 62)
            nn.ConvTranspose2d(num_feat_maps_gen * 4, num_feat_maps_gen * 2, kernel_size=4, stride=2, padding=0,
                               bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 2),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 2, 66, 126)
            nn.ConvTranspose2d(num_feat_maps_gen * 2, num_feat_maps_gen, kernel_size=4, stride=1, padding=(3, 2),
                               bias=False),
            nn.BatchNorm2d(num_feat_maps_gen),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen, 63, 125)
            nn.ConvTranspose2d(num_feat_maps_gen, color_channels, kernel_size=4, stride=1, padding=0, bias=False),
            # (color_channels = 13, 66, 128)
            nn.Tanh()
        )

    # load model parameters
    def load_model(self, model_dir: str):
        gen_state_dict = torch.load(model_dir)
        self.generator.load_state_dict(gen_state_dict)

    # generate an image
    def generate_image(self, latent_space):
        return self.generator(latent_space)


playground = Playground()
playground.draw()

if __name__ == '__main__':
    playground.mainloop()
