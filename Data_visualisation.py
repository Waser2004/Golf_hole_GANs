import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize
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
        self.image = (np.zeros((self.IMAGE_SIZE[1], self.IMAGE_SIZE[0], 3), dtype=np.int32) + 1) * 220

    # visualise data
    def visualise(self, poly_data: np.array, fade_data: np.array):
        # convert to image
        image = self.colors[poly_data]

        # create fairway / tee texture
        texture = self.create_diagonal_lines(8, [600, 400])
        # add texture to fairway
        image[(texture == 0) & np.all(image == self.colors[3], axis=2)] = [36, 168, 55]
        image = self.transform_1_to_2(image, 2, [36, 168, 55], self.colors[3])
        # add texture to tee
        image[(texture == 0) & np.all(image == self.colors[2], axis=2)] = [114, 171, 70]
        image = self.transform_1_to_2(image, 2, [114, 171, 70], self.colors[2])

        # upscale image
        self.image = resize(image, (900, 600), preserve_range=True, mode='constant').astype(np.int32)

        plt.imshow(self.image)
        plt.show()

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