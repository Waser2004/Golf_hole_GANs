import os
import random
import json
import time

from Data_converter import Data_converter
from PIL import Image
from Data_visualisation import Data_Visualiser
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as func
from torch.utils.data import Dataset
import numpy as np
from math import *

# --- Load the Data --- #
# Data parameters
GIRD_SIZE = (66, 128)
BOX_SIZE = 4

data_vis = Data_Visualiser(
    image_size=GIRD_SIZE,
    box_size=BOX_SIZE
)

data_conv = Data_converter(
    grid_size=GIRD_SIZE,
    box_size=BOX_SIZE
)

# convert data
DATA = data_conv.convert_all_procedural()

# Train Data / Log
TRAIN_DATA = np.array(DATA)


# Dataset
class CustomDataset(Dataset):
    def __init__(self, data, device):
        self.data = data
        self.device = device

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = torch.from_numpy(self.data[idx])
        sample.to(self.device)
        return sample


# --- DCGAN --- #
class DCGAN(torch.nn.Module):
    def __init__(self, load, backup, name, latent_dim=100, num_feat_maps_gen=32, num_feat_maps_dis=28, color_channels=13):
        super().__init__()

        self.generator = nn.Sequential(
            # (latent_dim, 1, 1)
            nn.ConvTranspose2d(latent_dim, num_feat_maps_gen * 16, kernel_size=12, stride=2, padding=4, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 16),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 16, 4, 4)
            nn.ConvTranspose2d(num_feat_maps_gen * 16, num_feat_maps_gen * 8, kernel_size=9, stride=2, padding=0, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 8, 15, 15)
            nn.ConvTranspose2d(num_feat_maps_gen * 8, num_feat_maps_gen * 8, kernel_size=7, stride=2, padding=2, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 4, 31, 31)
            nn.ConvTranspose2d(num_feat_maps_gen * 8, num_feat_maps_gen * 4, kernel_size=4, stride=(1, 2), padding=1, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 4),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 4, 32, 62)
            nn.ConvTranspose2d(num_feat_maps_gen * 4, num_feat_maps_gen * 2, kernel_size=4, stride=2, padding=0, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 2),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 4, 66, 126)
            nn.ConvTranspose2d(num_feat_maps_gen * 2, num_feat_maps_gen, kernel_size=4, stride=1, padding=(3, 2), bias=False),
            nn.BatchNorm2d(num_feat_maps_gen),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 4, 63, 125)
            nn.ConvTranspose2d(num_feat_maps_gen, color_channels, kernel_size=4, stride=1, padding=0, bias=False),
            # (color_channels = 13, 66, 128)
            nn.Tanh()
        )

        # load Generator parameters
        if load and backup is None:
            gen_state_dict = torch.load(f"D:/4. Programmieren/Golf_hole_GANs/Models/{name}/Generator.pth")
            self.generator.load_state_dict(gen_state_dict)
        elif backup is not None:
            gen_state_dict = torch.load(f"D:/4. Programmieren/Golf_hole_GANs/Models/{name}/Backups/Generator_{backup}.pth")
            self.generator.load_state_dict(gen_state_dict)

        self.discriminator = nn.Sequential(
            # (color_channels = 13, 66, 128)
            nn.Conv2d(color_channels, num_feat_maps_dis, kernel_size=12, stride=2, padding=1),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis, 31, 62)
            nn.Conv2d(num_feat_maps_dis, num_feat_maps_dis * 2, kernel_size=9, stride=2, padding=4, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 2),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 2, 15, 30)
            nn.Conv2d(num_feat_maps_dis * 2, num_feat_maps_dis * 4, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 4),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 4, 8, 15)
            nn.Conv2d(num_feat_maps_dis * 4, num_feat_maps_dis * 8, kernel_size=4, stride=(1, 2), padding=1, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 8, 7, 8)
            nn.Conv2d(num_feat_maps_dis * 8, num_feat_maps_dis * 16, kernel_size=4, stride=2, padding=2, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 16),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 16, 4, 4)
            nn.Conv2d(num_feat_maps_dis * 16, 1, kernel_size=4, stride=2, padding=1),
            # (1, 2, 2)
            nn.Flatten(),
            # (4)
            nn.Linear(4, 1)
            # (1)
        )

        # load discriminator parameters
        if load and backup is None:
            disc_state_dict = torch.load(f"D:/4. Programmieren/Golf_hole_GANs/Models/{name}/Discriminator.pth")
            self.discriminator.load_state_dict(disc_state_dict)
        # load backup
        elif backup is not None:
            disc_state_dict = torch.load(f"D:/4. Programmieren/Golf_hole_GANs/Models/{name}/Backups/Discriminator_{backup}.pth")
            self.discriminator.load_state_dict(disc_state_dict)

    def generator_forward(self, z):
        img = self.generator(z)
        return img

    def discriminator_forward(self, img):
        logits = self.discriminator(img)
        return logits


def generate_epoch_image(model, device, epoch):
    # generate image
    print("Create epoch-Image:")
    print("[{}] {}%".format("." * 20, 0), end="", flush=True)

    images = model.generator_forward(torch.load('Noise_Tensors/32d_perm_noise.pt').to(device))
    parent_image = np.zeros((4 * 128, 8 * 66, 3)).astype(np.uint8)

    converted_img = decode_data(images.detach()).astype(int)

    for i, image in enumerate(converted_img):
        # convert image
        converted_img = image.reshape(128, 66)
        visualised_img = data_vis.visualise(converted_img, hole_fade=False, high_res=False)

        # calc position
        x = round((i / 4 - floor(i / 4)) * 512)
        y = floor(i / 4) * 66

        # apply image
        parent_image[x:x + 128, y:y + 66] = visualised_img

        print("\r", end="")
        print(
            "[{}{}] {}%".format(
                "=" * floor(i / (len(images) - 1) * 20) if (len(images) - 1) > 0 else 20,
                "." * (20 - floor(i / (len(images) - 1) * 20)) if (len(images) - 1) > 0 else 0,
                i / (len(images) - 1) * 100) if (len(images) - 1) > 0 else 100,
            end="", flush=True
        )

    # save image
    print(epoch)
    image = Image.fromarray(parent_image)
    image.save(f'D:/4. Programmieren/Golf_hole_GANs/Generated_Images/{MODEL_NAME}/Epoch_{epoch}.png')

    print("\r", end="")
    print("[----- Complete -----] 100%")


# Training loop
def train(start_epoch, epochs, model, data, gen_optimizer, disc_optimizer, latent_space, device, prev_log, loss_fn = None):
    log = {
        "generator_loss": prev_log["generator_loss"] if prev_log is not None else [],
        "discriminator_loss": prev_log["discriminator_loss"] if prev_log is not None else [],
        "elapsed_epochs": start_epoch,
        "elapsed_time": prev_log["elapsed_time"] if prev_log is not None else []
    }

    if loss_fn is None:
        loss_fn = func.binary_cross_entropy_with_logits

    perm_noise = torch.load('Noise_Tensors/1d_perm_noise.pt').to(device)

    # visualisation
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 5))
    plt.ion()

    # epochs
    for epoch in range(epochs):
        start = time.time()

        model.train()

        # progress bar
        print(f"Epoch {epoch + start_epoch}:")
        print("[{}] {}%".format("." * 20, 0), end="", flush=True)

        # loop over each batch
        for batch_idx, features in enumerate(data):
            batch_size = features.size(0)

            # convert real data - use smooth labels
            real_images = encode_data(features, device, smooth=True)
            real_images.to(device)
            real_labels = flipped_fake_labels = torch.ones(batch_size, device=device)

            # generate fake images - use smooth labels
            noise = torch.randn(batch_size, latent_space, 1, 1, device=device)
            fake_images = model.generator_forward(noise)
            fake_labels = torch.zeros(batch_size, device=device)

            # --- train discriminator --- #
            disc_optimizer.zero_grad()

            # get discriminator loss on real images
            disc_prediction_real = model.discriminator_forward(real_images).view(-1)
            real_loss = loss_fn(disc_prediction_real, real_labels)

            # get discriminator loss on fake images
            disc_prediction_fake = model.discriminator_forward(fake_images.detach()).view(-1)
            fake_loss = loss_fn(disc_prediction_fake, fake_labels)

            # combined loss
            disc_loss = (real_loss + fake_loss) / 2
            disc_loss.backward()

            disc_optimizer.step()

            # --- train Generator --- #
            gen_optimizer.zero_grad()

            # get discriminator loss on fake images with flipped labels
            disc_prediction_fake = model.discriminator_forward(fake_images).view(-1)
            gen_loss = loss_fn(disc_prediction_fake, flipped_fake_labels)
            gen_loss.backward()

            gen_optimizer.step()

            # --- log and visualise --- #
            log["generator_loss"].append(gen_loss.detach().item())
            log["discriminator_loss"].append(disc_loss.detach().item())

            # update progress bar
            print("\r", end="")
            print(
                "[{}{}] {}%".format(
                    "=" * floor(batch_idx / (len(data) - 1) * 20) if (len(data) - 1) > 0 else 20,
                    "." * (20 - floor(batch_idx / (len(data) - 1) * 20)) if (len(data) - 1) > 0 else 0,
                    batch_idx / (len(data) - 1) * 100) if (len(data) - 1) > 0 else 100,
                end="", flush=True
            )

            # update loss plot
            ax1.clear()
            ax1.plot(log["generator_loss"], label='Generator Loss')
            ax1.plot(log["discriminator_loss"], label='Discriminator Loss')
            ax1.set_xlabel('Iterations')
            ax1.set_ylabel('Loss')
            ax1.set_title('GAN Losses')
            ax1.legend()

            # calculate images
            images = model.generator_forward(perm_noise)

            # update generated Hole image
            ax2.clear()
            ax2.imshow(decode_data(images.detach(), probability=True)[0], cmap='viridis', vmin=0, vmax=1)
            ax2.axis('off')
            ax2.set_title('Generated Image')

            # update generated Hole image
            ax3.clear()
            converted_img = decode_data(images.detach())[0].astype(int)
            converted_img = converted_img.reshape(128, 66)
            ax3.imshow(data_vis.visualise(converted_img, hole_fade=False, high_res=False))
            ax3.axis('off')
            ax3.set_title('Generated Image')

            plt.pause(0.0001)

        print("\r", end="")
        print("[----- Complete -----] 100%")

        log["elapsed_epochs"] += 1
        log["elapsed_time"].append(time.time() - start)

        # save backup
        if (epoch + 1 + start_epoch) % 10 == 0:
            torch.save(model.generator.state_dict(), f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/Backups/Generator_{epoch + 1 + start_epoch}.pth")
            torch.save(model.discriminator.state_dict(), f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/Backups/Discriminator_{epoch + 1 + start_epoch}.pth")

            with open(f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/Backups/log_{epoch + 1 + start_epoch}.json", 'w') as file:
                json.dump(log, file)

        # save Models
        torch.save(model.generator.state_dict(), f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/Generator.pth")
        torch.save(model.discriminator.state_dict(), f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/Discriminator.pth")

        # save log data
        with open(f'D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/log.json', 'w') as file:
            json.dump(log, file)

        # generate image
        generate_epoch_image(model, DEVICE, epoch + 1 + start_epoch)

        print(f"Generator loss: {log['generator_loss'][-1]}")
        print(f"Discriminator loss: {log['discriminator_loss'][-1]}")

    print("========== Training Complete ==========")
    print(f"Generator loss: {log['generator_loss']}")
    print(f"Discriminator loss: {log['discriminator_loss']}")

    plt.plot()

    return log


def encode_data(data, device, smooth=False):
    # image with 12 channels
    output_array = torch.zeros((data.shape[0], 13, data.shape[1], data.shape[2]), device=device) - 1
    # smoothen the data from -1 ~ -0.8
    if smooth:
        output_array += torch.randn((data.shape[0], 13, data.shape[1], data.shape[2]), device=device) * 0.1

    # get chanel positions
    img_indices = torch.arange(data.shape[0]).unsqueeze(1).unsqueeze(2)
    i_indices = torch.arange(data.shape[1]).unsqueeze(0).unsqueeze(-1)
    j_indices = torch.arange(data.shape[2]).unsqueeze(0).unsqueeze(0)

    # set active chanel to 1 | if smooth to 0.8 ~ 1
    output_array[img_indices, data, i_indices, j_indices] = 1 - (random.randint(0, 10) / 100) if smooth else 1
    output_array = output_array.permute(0, 1, 3, 2)

    return output_array


def decode_data(data, probability=False):
    # rearrange data and create new numpy array
    data = data.permute(0, 3, 2, 1)
    output_array = np.zeros((data.shape[0], data.shape[1], data.shape[2], 1))

    for img in range(data.shape[0]):
        # Convert the data tensor to a numpy array
        data_np = data[img].cpu().numpy()
        value = np.max(data_np, axis=2) if probability else np.argmax(data_np, axis=2)
        value = value.reshape((data.shape[1], data.shape[2], 1))
        # convert active chanel to integer
        output_array[img] = value

    return output_array


# --- GANs Parameters --- #
# load models
LOAD_MODELS = False
MODEL_NAME = "1. GreenSpace_Lite"
BACKUP = None
EPOCHS = 100
GENERATOR_LEARNING_RATE = 0.0003
DISCRIMINATOR_LEARNING_RATE = 0.0003

BATCH_SIZE = 256
LATENT_SPACE = 100
IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANNELS = GIRD_SIZE[0], GIRD_SIZE[1], 13

# load prev log
if os.listdir(f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}").count("log.json") and LOAD_MODELS and BACKUP is None:
    with open(f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/log.json", "r") as json_file:
        LOG = json.load(json_file)
        START_EPOCH = LOG["elapsed_epochs"]
# load backup
elif BACKUP is not None:
    with open(f"D:/4. Programmieren/Golf_hole_GANs/Models/{MODEL_NAME}/Backups/log_{BACKUP}.json", "r") as json_file:
        LOG = json.load(json_file)
        START_EPOCH = LOG["elapsed_epochs"]
# all new model
else:
    LOG = None
    START_EPOCH = 0

# Set the device (GPU or CPU)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("#########################################################################")
print(f"Using {torch.cuda.get_device_name(torch.cuda.current_device())} for Training the {MODEL_NAME} Network")
print("#########################################################################")

# GAN model
model = DCGAN(LOAD_MODELS, BACKUP, MODEL_NAME)
model.to(DEVICE)

# optimizers
optim_gen = torch.optim.Adam(model.generator.parameters(), betas=(0.5, 0.999), lr=GENERATOR_LEARNING_RATE)
optim_disc = torch.optim.Adam(model.discriminator.parameters(), betas=(0.5, 0.999), lr=DISCRIMINATOR_LEARNING_RATE)

# create dataset
dataset = CustomDataset(TRAIN_DATA, DEVICE)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

if START_EPOCH == 0:
    generate_epoch_image(model, DEVICE, START_EPOCH)

# train dataset
log = train(START_EPOCH, EPOCHS, model, dataloader, optim_gen, optim_disc, LATENT_SPACE, DEVICE, LOG)
