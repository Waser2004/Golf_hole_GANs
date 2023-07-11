import copy
from skimage.transform import resize
from Data_converter import Data_converter
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import scipy
from math import *


class Augmentation(object):
    def __init__(self):
        pass

    def augment_data(self, grid_size, box_size):
        # load data
        converter = Data_converter(grid_size=grid_size, box_size=box_size)
        data = converter.convert_all()

        print(len(data))

        # augment data
        augmented_data = []
        for d in data:
            augmented_data.append(d)
            for aug in self.auto_augment(d, box_size):
                augmented_data.append(aug)

        print(len(augmented_data))
        return augmented_data

    # auto augmentation
    def auto_augment(self, data, box_size):
        # calculate x_min and x_max
        hole_mask = np.argwhere(data != 0)
        x_min = 5 - np.min(hole_mask[:, 1])
        x_max = (data.shape[1] - 5) - np.max(hole_mask[:, 1])

        green_mask = np.where(data == 1, 1, 0)
        green_groups, num_groups = scipy.ndimage.label(green_mask)

        green_y_pos = []
        for i in range(num_groups):
            min_y = np.min(np.argwhere(green_groups == i + 1)[:, 0])
            max_y = np.max(np.argwhere(green_groups == i + 1)[:, 0])
            green_y_pos.append(min_y + (max_y - min_y) / 2)

        # calculate green center
        green_center = round(min(green_y_pos))

        # create tee distance marking
        tee_mask = np.where(data == 2, 1, 0)
        tee_groups, num_groups = scipy.ndimage.label(tee_mask)

        tee_y_pos = []
        for i in range(num_groups):
            min_y = np.min(np.argwhere(tee_groups == i + 1)[:, 0])
            max_y = np.max(np.argwhere(tee_groups == i + 1)[:, 0])
            tee_y_pos.append(min_y + (max_y - min_y) / 2)

        # calculate tee center
        tee_center = round(max(tee_y_pos))

        distance = tee_center - green_center

        y_min = 280 - distance * box_size
        y_max = 420 - distance * box_size

        # calculate augmentation values
        augmentations = []
        for x_stretch in range(9):
            if x_min <= x_stretch * 5 - 20 <= x_max:
                for y_stretch in range(9):
                    if y_min <= y_stretch * 5 - 20 <= y_max and not x_stretch == y_stretch == 0:
                        augmentations.append([x_stretch * 5 - 20, y_stretch * 5 - 20])

        return self.augment(data, augmentations)

    @staticmethod
    def augment(data, augmentation_values: list[[int, int]]):
        augmentations = []

        green_mask = np.where(data == 1, 1, 0)
        green_groups, num_groups = scipy.ndimage.label(green_mask)

        green_y_pos = []
        for i in range(num_groups):
            min_y = np.min(np.argwhere(green_groups == i + 1)[:, 0])
            max_y = np.max(np.argwhere(green_groups == i + 1)[:, 0])
            green_y_pos.append(min_y + (max_y - min_y) / 2)

        # calculate green center
        green_center = round(min(green_y_pos))

        # create tee distance marking
        tee_mask = np.where(data == 2, 1, 0)
        tee_groups, num_groups = scipy.ndimage.label(tee_mask)

        tee_y_pos = []
        for i in range(num_groups):
            min_y = np.min(np.argwhere(tee_groups == i + 1)[:, 0])
            max_y = np.max(np.argwhere(tee_groups == i + 1)[:, 0])
            tee_y_pos.append(min_y + (max_y - min_y) / 2)

        # calculate tee center
        tee_center = round(max(tee_y_pos))

        distance = tee_center - green_center

        # augment Data
        for x_value, y_value in augmentation_values:
            augmentations.append(copy.deepcopy(data))
            # calculate shift for each line
            for dis in range(distance):
                roll_val = floor((sin((dis * 2 * pi / distance) - (pi / 2)) + 1) * (x_value / 2))
                augmentations[-1][green_center + dis] = np.roll(augmentations[-1][green_center + dis], roll_val)

            # calculate shift for each line
            mask = np.round(
                resize(
                    augmentations[-1],
                    (data.shape[0] + round(y_value / 2) * 2, data.shape[1]),
                    order=0, mode='constant', anti_aliasing=False
                )
            )
            if data.shape[0] + round(y_value / 2) * 2 > augmentations[-1].shape[0]:
                augmentations[-1] = mask[round(y_value / 2):mask.shape[0] - round(y_value / 2)]
            else:
                augmentations[-1] = np.zeros_like(augmentations[-1])
                padding = floor((augmentations[-1].shape[0] - mask.shape[0]) / 2)
                augmentations[-1][padding:padding + mask.shape[0]] = mask

        # Normalize Data
        for aug_i, aug in enumerate(augmentations):
            # calc movement length
            hole_mask = np.argwhere(aug != 0)
            dy = floor((np.min(hole_mask[:, 0]) + (np.max(hole_mask[:, 0]) - np.min(hole_mask[:, 0])) / 2) - data.shape[0] / 2)
            dx = floor((np.min(hole_mask[:, 1]) + (np.max(hole_mask[:, 1]) - np.min(hole_mask[:, 1])) / 2) - data.shape[1] / 2)

            # move along x-axis
            mask = copy.deepcopy(aug)
            aug = np.zeros_like(aug)
            for column in range(mask.shape[1]):
                if column + dx < mask.shape[1]:
                    aug[:, column] = mask[:, column + dx]

            # move along y-axis
            mask = copy.deepcopy(aug)
            aug = np.zeros_like(aug)
            for row in range(mask.shape[0]):
                aug[row] = mask[row + dy]

            # apply changes
            augmentations[aug_i] = aug

        return augmentations
