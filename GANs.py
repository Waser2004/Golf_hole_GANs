import random
import json
from PIL import Image
from Data_converter import Data_converter
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
BOX_SIZE = 5

# initialise Converter and Visualiser
data_conv = Data_converter(
    grid_size=GIRD_SIZE,
    box_size=BOX_SIZE
)

data_vis = Data_Visualiser(
    image_size=GIRD_SIZE,
    box_size=BOX_SIZE
)

# convert all data
DATA = data_conv.convert_all_procedural()

# visualise the first picture
first_image = data_vis.visualise(
    poly_data=(DATA[12]).astype(int),
    high_res=False,
    hole_fade=True
)

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
    def __init__(self, latent_dim=100, num_feat_maps_gen=32, num_feat_maps_dis=32, color_channels=12):
        super().__init__()

        self.generator = nn.Sequential(
            # (latent_dim, 1, 1)
            nn.ConvTranspose2d(latent_dim, num_feat_maps_gen * 16, kernel_size=12, stride=1, padding=4, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 16),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 16, 4, 4)
            nn.ConvTranspose2d(num_feat_maps_gen * 16, num_feat_maps_gen * 8, kernel_size=9, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 8, 9, 9)
            nn.ConvTranspose2d(num_feat_maps_gen * 8, num_feat_maps_gen * 4, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 4),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 4, 17, 17)
            nn.ConvTranspose2d(num_feat_maps_gen * 4, num_feat_maps_gen * 2, kernel_size=4, stride=2, padding=2, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen * 2),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen * 2, 32, 32)
            nn.ConvTranspose2d(num_feat_maps_gen * 2, num_feat_maps_gen, kernel_size=4, stride=(1, 2), padding=1, bias=False),
            nn.BatchNorm2d(num_feat_maps_gen),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_gen, 33, 64)
            nn.ConvTranspose2d(num_feat_maps_gen, color_channels, kernel_size=4, stride=2, padding=1, bias=False),
            # (color_channels = 12, 66, 128)
            nn.Tanh()
        )

        self.discriminator = nn.Sequential(
            # (color_channels = 12, 66, 128)
            nn.Conv2d(color_channels, num_feat_maps_dis, kernel_size=12, stride=2, padding=3),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis, 31, 62)
            nn.Conv2d(num_feat_maps_dis, num_feat_maps_dis * 2, kernel_size=9, stride=2, padding=5, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 2),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 2, 17, 32)
            nn.Conv2d(num_feat_maps_dis * 2, num_feat_maps_dis * 4, kernel_size=7, stride=(1, 2), padding=2, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 4),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 4, 15, 15)
            nn.Conv2d(num_feat_maps_dis * 4, num_feat_maps_dis * 8, kernel_size=4, stride=2, padding=2, bias=False),
            nn.BatchNorm2d(num_feat_maps_dis * 8),
            nn.LeakyReLU(inplace=True),
            # (num_feat_maps_dis * 4, 8, 8)
            nn.Conv2d(num_feat_maps_dis * 8, 1, kernel_size=4, stride=2, padding=0),
            # (1, 2, 2)
            nn.Flatten(),
            # (9)
            nn.Linear(9, 1)
            # (1)
        )

    def generator_forward(self, z):
        img = self.generator(z)
        return img

    def discriminator_forward(self, img):
        logits = self.discriminator(img)
        return logits


# Training loop
def train(start_epoch, epochs, model, data, gen_optimizer, disc_optimizer, latent_space, device, loss_fn = None):
    log = {
        "generator_loss": [],
        "discriminator_loss": [],
    }

    if loss_fn is None:
        loss_fn = func.binary_cross_entropy_with_logits

    perm_noise = torch.randn(1, latent_space, 1, 1, device=device)
    perm_435_noise = torch.randn(435, latent_space, 1, 1, device=device)

    # visualisation
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 5))
    plt.ion()

    # epochs
    for epoch in range(epochs):
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
            real_labels = flipped_fake_labels = torch.ones(batch_size, device=device) - torch.randn(batch_size, device=device) / 10

            # generate fake images - use smooth labels
            noise = torch.randn(batch_size, latent_space, 1, 1, device=device)
            fake_images = model.generator_forward(noise)
            fake_labels = torch.zeros(batch_size, device=device) + torch.randn(batch_size, device=device) / 10

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

        # generate image
        print("Create epoch-Image:")
        print("[{}] {}%".format("." * 20, 0), end="", flush=True)

        images = model.generator_forward(perm_435_noise)
        parent_image = np.zeros((15 * 128, 29 * 66, 3)).astype(np.uint8)

        for i, image in enumerate(images):
            # convert image
            converted_img = decode_data(image.detach())[0].astype(int)
            converted_img = converted_img.reshape(128, 66)
            visualised_img = data_vis.visualise(converted_img, hole_fade=False, high_res=False)

            # calc position
            x = round((i / 15 - floor(i / 15)) * 1920)
            y = floor(i / 15) * 66

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
        image = Image.fromarray(parent_image)
        image.save(f'Generator_images/Epoch_{epoch}')

        print("\r", end="")
        print("[----- Complete -----] 100%")

        print(f"Generator loss: {log['generator_loss'][-1]}")
        print(f"Discriminator loss: {log['discriminator_loss'][-1]}")

    print("========== Training Complete ==========")
    print(f"Generator loss: {log['generator_loss']}")
    print(f"Discriminator loss: {log['discriminator_loss']}")

    plt.plot()

    return log


def encode_data(data, device, smooth=False):
    # image with 12 channels
    output_array = torch.zeros((data.shape[0], 12, data.shape[1], data.shape[2]), device=device) - 1
    # smoothen the data from -1 ~ -0.8
    if smooth:
        output_array += torch.randn((data.shape[0], 12, data.shape[1], data.shape[2]), device=device) * 0.1

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
START_EPOCH = 0
EPOCHS = 500
GENERATOR_LEARNING_RATE = 0.0004
DISCRIMINATOR_LEARNING_RATE = 0.0001

BATCH_SIZE = 256
LATENT_SPACE = 100
IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_CHANNELS = GIRD_SIZE[0], GIRD_SIZE[1], 12

# Set the device (GPU or CPU)
print(torch.cuda.is_available())
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# GAN model
model = DCGAN()
model.to(DEVICE)

# optimizers
optim_gen = torch.optim.Adam(model.generator.parameters(), betas=(0.5, 0.999), lr=GENERATOR_LEARNING_RATE)
optim_disc = torch.optim.Adam(model.discriminator.parameters(), betas=(0.5, 0.999), lr=DISCRIMINATOR_LEARNING_RATE)

# create dataset
dataset = CustomDataset(TRAIN_DATA, DEVICE)
dataset = dataset
dataloader = torch.utils.data.DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# train dataset
log = train(START_EPOCH, EPOCHS, model, dataloader, optim_gen, optim_disc, LATENT_SPACE, DEVICE)

torch.save(model.generator.state_dict(), "Models/Base_Generator.pth")
torch.save(model.discriminator.state_dict(), "Models/Base_Discriminator.pth")

# save log data
with open(f'Models/log_{START_EPOCH}_to_{START_EPOCH + EPOCHS}.json', 'w') as file:
    json.dump(log, file)
