import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize
import scipy.ndimage
from skimage.measure import label
from PIL import Image
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
    def visualise(self, poly_data: np.array, high_res: bool = False, hole_fade: bool = False):
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
        image = resize(image, (self.IMAGE_SIZE[1], self.IMAGE_SIZE[0]), preserve_range=True, mode='constant').astype(np.int32)

        if hole_fade:
            # calculate opacity
            hole_mask = np.where(np.all(image == np.array([220, 220, 220]), axis=-1), 0, 1)
            hole_mask = self.calc_dist_map(hole_mask)

            fade_dis = 10 / self.BOX_SIZE / (poly_data.shape[0] / image.shape[0])
            hole_mask = np.where(hole_mask > fade_dis, fade_dis, hole_mask) / fade_dis

            # reshape opacity
            hole_mask = np.expand_dims(hole_mask, axis=2)
            hole_mask = np.repeat(hole_mask, 3, axis=2)

            # Create the new combined image
            image = np.array([210, 210, 210]) * (np.array([1, 1, 1]) - hole_mask) + image * hole_mask
            image = image.astype(np.int32)

        # upscale image
        self.image = image

        # Convert the NumPy array to an image
        image = Image.fromarray(self.image.astype('uint8'))

        # Save the image to a file
        image.save('image.png')

        plt.imshow(self.image)
        plt.show()

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
