import copy
import tkinter as tk
import tkinter.filedialog
from tkinter.font import Font
from Data_visualisation import Data_Visualiser
from skimage.transform import resize
import torch.nn as nn
import numpy as np
import PIL as pil
from PIL import Image, ImageTk
import os
import torch
import threading
from Canvas_Objects import *


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
        self.model_sel_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 - 200, 10],
                                        [self.WINDOW_SIZE[0] // 2 + 200, 60], 10, [240, 240, 240], 0, [0, 0, 0])
        self.model_sel_folder_back = Rectangle(self.canvas, [self.WINDOW_SIZE[0] // 2 + 150, 10],
                                               [self.WINDOW_SIZE[0] // 2 + 200, 60], 10, [240, 240, 240], 0, [0, 0, 0])
        img = pil.ImageTk.PhotoImage(pil.Image.open("Icons/folder.png"))
        self.model_sel_folder_img = Image(self.canvas, img, [self.WINDOW_SIZE[0] // 2 + 175, 35])
        self.model_sel_model_label = Text(self.canvas, "Select Model", [self.WINDOW_SIZE[0] // 2 - 180, 35],
                                          [25, 25, 25], font_size=20, anchor=tk.W)
        self.model_sel_gener_label = Text(self.canvas, "Generate image", [self.WINDOW_SIZE[0] // 2 - 180, 30],
                                          [240, 240, 240], font_size=20, anchor=tk.W)

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
        self.animation_menu = False
        self.current_time_step = 0
        self.max_time_steps = 250
        self.time_step_line = Line(self.canvas, [self.WINDOW_SIZE[0] - 25, 50], [self.WINDOW_SIZE[0] - 25, self.WINDOW_SIZE[1] - 50], [150, 150, 150], 1)
        self.time_step_indication = Circle(self.canvas, [self.WINDOW_SIZE[0] - 25, (self.WINDOW_SIZE[1] - 100) / self.max_time_steps * self.current_time_step + 50], 3, [150, 150, 150], 0, [150, 150, 150])

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
        self.root.bind('<Button-1>', self.button_1)
        self.root.bind('<B1-Motion>', self.button_1_motion)
        self.root.bind('<ButtonRelease-1>', self.button_1_release)
        self.root.bind('<MouseWheel>', self.mouse_wheel)
        self.root.bind('<Key>', self.key)
        self.root.bind_class("Tk", "<Configure>", self.resize)

    def draw(self):
        # draw generated image
        self.generated_image.draw()

        # draw model selection
        self.model_sel_folder_back.draw()
        self.model_sel_folder_img.draw()
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

        self.visualise_latent()

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

    # left click
    def button_1(self, event):
        self.last_click_pos = [event.x, event.y]
        self.reset_slider()

        # select model
        if (self.model_sel_back.is_pressed(event.x, event.y) and self.model_sel_model_label.text == "Select Model") or \
                self.model_sel_folder_back.is_pressed(event.x, event.y):
            # clear images
            placeholder = self.images["Placeholder"]
            self.images.clear()
            self.images.update({"Placeholder": placeholder})
            self.image_key = "Placeholder"

            # load model
            model = tk.filedialog.askopenfilename(initialdir="D:/4. Programmieren/Golf_hole_GANs/Models",
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
                    self.model_sel_model_label.set_center([self.WINDOW_SIZE[0] // 2 - 180, 46], animation=True,
                                                          animation_time=0.2)
                    self.model_sel_model_label.set_font_size(11, animation=True, animation_time=0.2)
                    self.model_sel_back.set_pos([self.WINDOW_SIZE[0] // 2 - 200, 10],
                                                [self.WINDOW_SIZE[0] // 2 + 140, 60],
                                                animation=True, animation_time=0.2)
                    self.model_sel_back.set_color([73, 182, 91], animation=True, animation_time=0.2)

                    self.model_loaded = True

                # load model
                self.model.load_model(model)
                thread = threading.Thread(target=lambda: self.generate_image(set_as_vis=True))
                self.canvas.after(1000, lambda: thread.start())

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

    def button_1_release(self, event):
        # point was selected
        if self.slider_pressed is not None:
            self.slider_pressed = None

            # update image
            if self.auto_gen and self.model_loaded:
                thread = threading.Thread(target=lambda: self.generate_image(set_as_vis=True))
                thread.start()

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
        # change slider label
        if self.edit_slider:
            if event.char == '0':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "0")))
            elif event.char == '1':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "1")))
            elif event.char == '2':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "2")))
            elif event.char == '3':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "3")))
            elif event.char == '4':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "4")))
            elif event.char == '5':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "5")))
            elif event.char == '6':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "6")))
            elif event.char == '7':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "7")))
            elif event.char == '8':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "8")))
            elif event.char == '9':
                # update label
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(str(int(self.latent_sliders[self.edit_slider_key[0]][3].text + "9")))

            elif event.keysym == 'Delete' or event.keysym == 'BackSpace' and len(self.latent_sliders[self.edit_slider_key[0]][3].text) >= 1:
                self.latent_sliders[self.edit_slider_key[0]][3].set_text(self.latent_sliders[self.edit_slider_key[0]][3].text[:-1])

            if event.keysym == 'Return':
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

            elif event.keysym == "Escape":
                self.reset_slider()

            else:
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
                elif self.latent_sliders[self.edit_slider_key[0]][1].color == [215, 64, 64]:
                    self.latent_sliders[self.edit_slider_key[0]][1].set_color([205, 205, 205], animation=True, animation_time=0.2)

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
            self.model_sel_back.set_pos([self.WINDOW_SIZE[0] // 2 - 200, 10], [self.WINDOW_SIZE[0] // 2 + 140, 60])
            self.model_sel_model_label.set_center([self.WINDOW_SIZE[0] // 2 - 180, 46])
            self.model_sel_gener_label.set_center([self.WINDOW_SIZE[0] // 2 - 180, 30])
            self.model_sel_folder_back.set_pos([self.WINDOW_SIZE[0] // 2 + 150, 10],
                                               [self.WINDOW_SIZE[0] // 2 + 200, 60])
            self.model_sel_folder_img.set_center([self.WINDOW_SIZE[0] // 2 + 175, 35])
        else:
            self.model_sel_back.set_pos([self.WINDOW_SIZE[0] // 2 - 200, 10], [self.WINDOW_SIZE[0] // 2 + 200, 60])
            self.model_sel_model_label.set_center([self.WINDOW_SIZE[0] // 2 - 180, 35])
            self.model_sel_gener_label.set_center([self.WINDOW_SIZE[0] // 2 - 180, 30])
            self.model_sel_folder_back.set_pos([self.WINDOW_SIZE[0] // 2 + 150, 10],
                                               [self.WINDOW_SIZE[0] // 2 + 200, 60])
            self.model_sel_folder_img.set_center([self.WINDOW_SIZE[0] // 2 + 175, 35])

        # resize generated image
        self.generated_image.set_center([self.WINDOW_SIZE[0] // 2, self.WINDOW_SIZE[1] // 2])
        self.visualise_generated_image()

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
