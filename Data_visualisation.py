import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize
from skimage.measure import label
from PIL import Image
from math import *


class Data_Visualiser(object):
    def __init__(self, image_size: [int, int]):
        # set grid parameters
        self.IMAGE_SIZE = image_size

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
        self.occ = np.zeros((self.IMAGE_SIZE[1], self.IMAGE_SIZE[0]), dtype=np.int32)
        self.image = np.zeros((self.IMAGE_SIZE[1], self.IMAGE_SIZE[0], 3), dtype=np.int32) + 220

    # visualise data
    def visualise(self, poly_data: np.array, fade_data: np.array, fade: bool = True, high_res: bool = True):
        # convert to image
        image = self.colors[poly_data]

        # add fade lines to image
        fade_image = self.colors[fade_data]
        image = np.where(fade_image != self.colors[0], self.colors[fade_data], image)

        # occupancy
        self.occ = np.where(image != self.colors[0], 1, 0)

        # create fairway / tee texture
        texture = self.create_diagonal_lines(6, [600, 400])
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
            bunker_mask = np.where(poly_data == 6, 0, bunker_mask)

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
            tree_mask = np.where(poly_data == 8, 0, tree_mask)

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

        if fade:
            # loop over each group
            for group_index in np.unique(poly_data):
                # only if the group index is bigger than 0
                if group_index > 0:
                    # create a mask
                    group_mask = np.zeros_like(poly_data)
                    group_mask[poly_data == group_index] = 1

                    # fade mask
                    fade_mask = np.zeros_like(poly_data)
                    fade_mask[(group_mask == 1) & (fade_data == group_index)] = 1

                    # continue on only if there even is a fade
                    if np.max(fade_mask) > 0:
                        self.draw_fade(self.occ, image, group_mask, group_index, fade_mask, 8)

        # upscale image
        self.image = resize(image, (900, 600), preserve_range=True, mode='constant').astype(np.int32)

        # # Convert the NumPy array to an image
        # image = Image.fromarray(self.image.astype('uint8'))

        #
        # # Save the image to a file
        # image.save('image.png')

        plt.imshow(self.image)
        plt.show()

    # generate outer gradiant line
    def draw_fade(self, depth: np.array, image: np.array, poly_mask: np.array, poly_index: int, fade_data: np.array, fade_length: int):
        # group the fade
        fade_groups = label(fade_data, connectivity=2)

        plt.imshow(fade_data)
        plt.show()

        # loop over fades
        for fade_index in np.unique(fade_groups):
            # only if the group index is bigger than 0
            if fade_index > 0:
                # create fade mask
                fade_mask = np.zeros_like(fade_data)
                fade_mask[fade_groups == fade_index] = 1

                # calculate distance map
                ones_indices = np.argwhere(fade_mask == 1)
                rows, cols = np.indices(fade_mask.shape)
                dist_array = np.sqrt((rows[:, :, np.newaxis] - ones_indices[:, 0]) ** 2 +
                                     (cols[:, :, np.newaxis] - ones_indices[:, 1]) ** 2)
                dist_array = np.min(dist_array, axis=-1)
                dist_array = np.where(dist_array > fade_length, fade_length + 1, dist_array)
                dist_array /= fade_length + 1

                # remove all the pixels that would intersect with the already drawn
                dist_mask = np.all(depth != 1, axis=-1)
                dist_array = np.where(dist_mask, dist_array, 1)

                new_values = image * dist_array[..., np.newaxis] + self.colors[poly_index] * (1 - dist_array[..., np.newaxis])
                image[:] = new_values
            else:
                # create fade mask
                fade_mask = np.zeros_like(fade_data)
                fade_mask[fade_groups == fade_index] = 1

                plt.imshow(fade_mask)
                plt.show()

    # calculate distance
    @staticmethod
    def calc_dist_map(mask: np.array):
        ones_indices = np.argwhere(mask == 1)
        rows, cols = np.indices(mask.shape)
        dist_array = np.sqrt((rows[:, :, np.newaxis] - ones_indices[:, 0]) ** 2 +
                             (cols[:, :, np.newaxis] - ones_indices[:, 1]) ** 2)
        dist_array = np.min(dist_array, axis=-1)

        # return
        return dist_array

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
