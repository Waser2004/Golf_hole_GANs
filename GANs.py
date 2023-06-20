from Data_converter import Data_converter
from Data_visualisation import Data_Visualiser
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np

# use gpu
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)
tf.config.set_visible_devices(physical_devices[0], 'GPU')

# --- Load the Data --- #
# Data parameters
GIRD_SIZE = (40, 60)
BOX_SIZE = 10

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
DATA = data_conv.convert_all()

# visualise the first picture
first_image = data_vis.visualise(
    poly_data=(DATA[0] * 12).astype(int),
    high_res=False,
    hole_fade=True
)

plt.imshow(first_image)
plt.show()


# Generator
def build_generator(latent_dim: int, output_shape: tuple[int, int]):
    assert output_shape[0] % 4 == 0 and output_shape[1] % 4 == 0, "not suitable output shape"

    model = tf.keras.Sequential()

    # Input: Random noise
    model.add(layers.Dense(output_shape[0] // 4 * output_shape[1] // 4 * 32, use_bias=False, input_shape=(latent_dim,)))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    # Reshape to a 3D tensor
    model.add(layers.Reshape((output_shape[0] // 4, output_shape[1] // 4, 32)))

    # Up-sampling layers
    model.add(layers.Conv2DTranspose(16, (5, 5), strides=(1, 1), padding='same', use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    # Up-sampling layers
    model.add(layers.Conv2DTranspose(8, (5, 5), strides=(2, 2), padding='same', use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    # Up-sampling layers
    model.add(layers.Conv2DTranspose(4, (5, 5), strides=(2, 2), padding='same', use_bias=False))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(1, 1), padding='same', use_bias=False, activation='sigmoid'))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    return model


# generator loss
def generator_loss(fake_output):
    return cross_entropy(tf.ones_like(fake_output), fake_output)


# Discriminator
def build_discriminator(input_shape: tuple[int, int]):
    model = tf.keras.Sequential()

    model.add(layers.Conv2D(4, (5, 5), strides=(2, 2), padding='same', input_shape=(input_shape[0], input_shape[1], 1)))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(2, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Flatten())
    model.add(layers.Dense(32, activation='relu'))

    model.add(layers.Dense(1, activation='sigmoid'))

    return model


# discriminator loss
def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss


# one training step
@tf.function
def train_step(images):
    noise = tf.random.normal([BATCH_SIZE, latent_dimension])

    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        # generate fakes
        generated_images = generator(noise, training=True)

        # predict truth of images
        real_output = discriminator(images, training=True)
        fake_output = discriminator(generated_images, training=True)

        # calculate loss
        gen_loss = generator_loss(fake_output)
        disc_loss = discriminator_loss(real_output, fake_output)

    # calculate model gradients
    gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
    gradients_of_discriminator = disc_tape.gradient(disc_loss, discriminator.trainable_variables)

    # optimize
    generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, discriminator.trainable_variables))

    return gen_loss, disc_loss


# training loop
def train(dataset, epochs):
    noise = tf.random.normal([1, latent_dimension])

    gen_losses = []
    disc_losses = []
    iterations = []

    # Create the figure and axis for the plot and image
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    for epoch in range(epochs):
        gen_loss = 0
        disc_loss = 0

        for i, image_batch in enumerate(dataset):
            gl, dl = train_step(image_batch)

            gen_loss = (gen_loss * i + gl) / (i + 1)
            disc_loss = (disc_loss * i + dl) / (i + 1)

        gen_losses.append(gen_loss)
        disc_losses.append(disc_loss)

        iterations.append(epoch)

        # Update the plot
        ax1.clear()
        ax1.plot(iterations, gen_losses, label='Generator Loss')
        ax1.plot(iterations, disc_losses, label='Discriminator Loss')
        ax1.set_xlabel('Iterations')
        ax1.set_ylabel('Loss')
        ax1.set_title('GAN Losses')
        ax1.legend()

        if epoch % 10 == 0:
            # generate image
            image = generator(noise)[0]
            # Update the image plot
            ax2.clear()
            ax2.imshow(image)
            ax2.axis('off')
            ax2.set_title('Generated Image')

        # Pause to allow the plot to be updated
        plt.pause(0.0001)

    plt.show()

    return gen_losses, disc_losses

# training parameters
BATCH_SIZE = 24
EPOCHS = 10000
latent_dimension = 600
num_examples_to_generate = 16

losses = []
# visualisation
latent_dimension += 5

# batch dataset
train_dataset = tf.data.Dataset.from_tensor_slices(DATA).batch(BATCH_SIZE)

# Create generator / discriminator
generator = build_generator(latent_dim=latent_dimension, output_shape=DATA[0].shape)
discriminator = build_discriminator(input_shape=DATA[0].shape)

# optimizers
generator_optimizer = tf.keras.optimizers.Adam(1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

losses.append(train(train_dataset, EPOCHS))

