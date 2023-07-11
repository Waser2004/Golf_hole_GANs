import copy

import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize
import scipy.ndimage
from skimage.measure import label
import scipy.ndimage
from PIL import Image, ImageDraw, ImageFont
from math import *


class Data_Visualiser(object):
    def __init__(self, image_size: [int, int], box_size: float):
        # set grid parameters
        self.IMAGE_SIZE = image_size
        self.BOX_SIZE = box_size

        # colors
        self.colors = np.array([
            [220, 220, 220],  # background color
            [50, 205, 50],
            [104, 155, 64],
            [33, 153, 50],
            [20, 101, 33],
            [17, 76, 25],
            [210, 180, 140],
            [240, 230, 140],
            [17, 48, 25],
            [70, 130, 180],
            [255, 255, 255],
            [128, 128, 128],
            [226, 114, 91]
        ])

        # create image
        self.image = np.zeros((self.IMAGE_SIZE[1], self.IMAGE_SIZE[0], 3), dtype=np.int32) + 220

    # visualise data
    def visualise(self, poly_data: np.array, high_res: bool = False, hole_fade: bool = False, description: bool = False):
        # convert to image
        image = self.colors[poly_data]

        # create fairway / tee texture
        texture = self.create_diagonal_lines(6, poly_data.shape)
        # add texture to fairway
        image[(texture == 0) & np.all(image == self.colors[3], axis=2)] = [36, 168, 55]
        image = self.transform_1_to_2(image, 2, [36, 168, 55], self.colors[3])
        # add texture to tee
        image[(texture == 0) & np.all(image == self.colors[2], axis=2)] = [114, 171, 70]
        image = self.transform_1_to_2(image, 2, [114, 171, 70], self.colors[2])

        if high_res:
            # texture bunker
            bunker_mask = self.calc_dist_map(np.where(poly_data == 6, 1, 0))
            bunker_mask = np.where(bunker_mask > 2, 2, 1)
            bunker_mask = np.where(poly_data != 6, 0, bunker_mask)

            # calculate distances
            bunker_mask = self.calc_dist_map(bunker_mask)
            bunker_mask = np.where(bunker_mask > 2.5, 2.5, bunker_mask) / 2.5

            # normalize bunker mask
            bunker_mask = np.where(poly_data != 6, 0, bunker_mask)
            bunker_mask = np.where((bunker_mask < 1) & (bunker_mask > 0), bunker_mask + (1 - bunker_mask) / 2, bunker_mask)

            # create texture
            bunker_texture = (bunker_mask[:, :, np.newaxis] * self.colors[6]).astype(np.uint8)

            # apply to image
            image = np.where(bunker_texture == np.array([0, 0, 0], dtype=np.uint8), image, bunker_texture)

            # texture trees
            tree_mask = self.calc_dist_map(np.where(poly_data == 8, 1, 0))
            tree_mask = np.where(tree_mask > 2, 2, 1)
            tree_mask = np.where(poly_data != 8, 0, tree_mask)

            # calculate distances
            tree_mask = self.calc_dist_map(tree_mask)
            tree_mask = np.where(tree_mask > 2.5, 2.5, tree_mask) / 2.5

            # normalize tree mask
            tree_mask = np.where(poly_data != 8, 0, tree_mask)
            tree_mask = np.where((tree_mask < 1) & (tree_mask > 0), 2 - tree_mask, tree_mask)

            # create texture
            tree_texture = (tree_mask[:, :, np.newaxis] * self.colors[8]).astype(np.uint8)

            # apply to image
            image = np.where(tree_texture == np.array([0, 0, 0], dtype=np.uint8), image, tree_texture)

        # upscale image
        image = resize(image, (self.IMAGE_SIZE[1], self.IMAGE_SIZE[0]), order=0, mode='constant', anti_aliasing=False).astype(np.int32)

        if hole_fade:
            # calculate opacity
            hole_mask = np.where(np.all(image == np.array([220, 220, 220]), axis=-1), 0, 1)
            hole_mask = self.calc_dist_map(hole_mask)

            fade_dis = 10 / self.BOX_SIZE / (poly_data.shape[0] / image.shape[0])
            hole_mask = np.where(hole_mask > fade_dis, fade_dis, hole_mask) / fade_dis

            # reshape opacity
            hole_mask_expanded = copy.deepcopy(hole_mask)
            hole_mask_expanded = np.expand_dims(hole_mask_expanded, axis=2)
            hole_mask_expanded = np.repeat(hole_mask_expanded, 3, axis=2)

            # Create the new combined image
            image = np.array([210, 210, 210]) * (np.array([1, 1, 1]) - hole_mask_expanded) + image * hole_mask_expanded
            image = image.astype(np.int32)

        if description:
            # create green distance marking
            green_mask = np.where(np.all(self.colors[poly_data] == np.array(self.colors[1]), axis=-1), 1, 0)
            green_groups, num_groups = scipy.ndimage.label(green_mask)

            green_y_pos = []
            for i in range(num_groups):
                min_y = np.min(np.argwhere(green_groups == i + 1)[:, 0])
                max_y = np.max(np.argwhere(green_groups == i + 1)[:, 0])
                green_y_pos.append(min_y + (max_y - min_y) / 2)

            # calculate green center
            green_center = min(green_y_pos)

            # create tee distance marking
            tee_mask = np.where(np.all(self.colors[poly_data] == np.array(self.colors[2]), axis=-1), 1, 0)
            tee_groups, num_groups = scipy.ndimage.label(tee_mask)

            tee_y_pos = []
            for i in range(num_groups):
                min_y = np.min(np.argwhere(tee_groups == i + 1)[:, 0])
                max_y = np.max(np.argwhere(tee_groups == i + 1)[:, 0])
                tee_y_pos.append(min_y + (max_y - min_y) / 2)

            # calculate tee center
            tee_center = max(tee_y_pos)

            # calculated distance
            y_ratio = self.IMAGE_SIZE[1] / poly_data.shape[0]
            distance = (tee_center - green_center) * self.BOX_SIZE

            # initialise drawer
            pil_image = Image.fromarray(image.astype(np.uint8))
            draw = ImageDraw.Draw(pil_image)

            # support lines
            pos = tee_center
            counter = 0
            while pos > 0:
                if counter % 5 == 0:
                    draw.line([(0, pos * y_ratio), (15, pos * y_ratio)], fill=(100, 100, 100), width=1)
                else:
                    draw.line([(0, pos * y_ratio), (10, pos * y_ratio)], fill=(100, 100, 100), width=1)
                counter += 1
                pos -= 10 / self.BOX_SIZE

            pos = tee_center
            counter = 0
            while pos < poly_data.shape[0]:
                if counter % 5 == 0:
                    draw.line([(0, pos * y_ratio), (15, pos * y_ratio)], fill=(100, 100, 100), width=1)
                else:
                    draw.line([(0, pos * y_ratio), (10, pos * y_ratio)], fill=(100, 100, 100), width=1)
                counter += 1
                pos += 10 / self.BOX_SIZE

            # tee indication
            draw.line([(0, tee_center * y_ratio), (20, tee_center * y_ratio)], fill=(0, 0, 0), width=2)
            font = ImageFont.truetype("Fonts/Roboto/Roboto-Black.ttf", 10)
            draw.text((25, tee_center * y_ratio - 6), "0", font=font, fill=(0, 0, 0))

            # green indication
            draw.line([(0, green_center * y_ratio), (20, green_center * y_ratio)], fill=(0, 0, 0), width=2)
            font = ImageFont.truetype("Fonts/Roboto/Roboto-Black.ttf", 10)
            draw.text((25, green_center * y_ratio - 6), f"{floor(distance)}", font=font, fill=(0, 0, 0))

            # calculate head_space
            hole_mask = np.where(np.all(self.colors[poly_data] == np.array([220, 220, 220]), axis=-1), 0, 1)
            head_space = np.min(np.argwhere(hole_mask == 1)[:, 0]) * y_ratio

            h1_space = floor((head_space - 8) * 0.6)
            h2_space = floor((head_space - 8) * 0.4)

            # draw heading
            font = ImageFont.truetype("Fonts/Roboto/Roboto-Black.ttf", h1_space if h1_space < 30 else 30)
            draw.text((25, 4), "Par 4", font=font, fill=(0, 0, 0))
            font = ImageFont.truetype("Fonts/Roboto/Roboto-Thin.ttf", h2_space if h2_space < 20 else 20)
            draw.text((25, 4 + h1_space if h1_space < 30 else 30), f"{floor(distance)} Meter", font=font, fill=(0, 0, 0))

            image = np.array(pil_image)

        # upscale image
        self.image = image

        # return image
        return self.image

    # calculate distance
    @staticmethod
    def calc_dist_map(mask: np.array):
        # Compute the distance transform of the binary mask
        dist_map = scipy.ndimage.distance_transform_edt(mask)

        # Return the distance map
        return dist_map

    # create fairway / tee texture
    @staticmethod
    def create_diagonal_lines(stroke_width: int, dimensions: list[int, int]):
        # Create a meshgrid of x and y coordinates
        x, y = np.meshgrid(np.arange(dimensions[1]), np.arange(dimensions[0]))

        # Calculate the distance from the current position to the nearest diagonal line
        distances = np.floor((x + y) / stroke_width)

        # Set the values of the array to 1 where the distance is odd, and 0 otherwise
        arr = (distances % 2 == 1).astype(int)

        return arr

    # convert edges of fairway / tee to darker color
    @staticmethod
    def transform_1_to_2(arr: np.array, r: int, color_1: np.array, color_2: np.array):
        # Create a copy of the input array to store the result
        result = np.copy(arr)

        # Get the dimensions of the input array
        rows, cols, _ = arr.shape

        # Iterate over each element in the input array
        for i in range(rows):
            for j in range(cols):
                # Check if the current color is color_1
                if np.all(arr[i, j] == color_1):
                    # Get the surrounding subarray with radius r
                    subarray = arr[max(0, i - r):min(rows, i + r + 1), max(0, j - r):min(cols, j + r + 1)]

                    # Check if any color in the surrounding subarray is not color_1 or color_2
                    if np.any(~(np.all(subarray == color_1, axis=-1) | np.all(subarray == color_2, axis=-1))):
                        # Replace the color with color_2 in the result array
                        result[i, j] = color_2

        return result
