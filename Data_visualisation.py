import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize


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

        # upscale image
        self.image = resize(image, (900, 600), preserve_range=True, mode='constant').astype(np.int32)

        plt.imshow(self.image)
        plt.show()

    # color lookup function
    def color_lookup(self, index: int):
        return np.array(self.colors[index], dtype=np.int32)
