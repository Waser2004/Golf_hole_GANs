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
GIRD_SIZE = (136, 200)
BOX_SIZE = 3

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
    model.add(layers.Dense(output_shape[0] // 4 * output_shape[1] // 4 * 16, use_bias=False, input_shape=(latent_dim,)))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    # Reshape to a 3D tensor
    model.add(layers.Reshape((output_shape[0] // 4, output_shape[1] // 4, 16)))

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

    model.add(layers.Conv2D(2, (5, 5), strides=(2, 2), padding='same', input_shape=(input_shape[0], input_shape[1], 1)))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(4, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))

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


# training loop
def train(dataset, epochs):
    for epoch in range(epochs):
        print(epoch)
        for image_batch in dataset:
            train_step(image_batch)

# training parameters
BATCH_SIZE = 16
EPOCHS = 50
latent_dimension = 100
num_examples_to_generate = 16

# batch dataset
train_dataset = tf.data.Dataset.from_tensor_slices(DATA).batch(BATCH_SIZE)

# Create generator / discriminator
generator = build_generator(latent_dim=latent_dimension, output_shape=DATA[0].shape)
discriminator = build_discriminator(input_shape=DATA[0].shape)

# optimizers
generator_optimizer = tf.keras.optimizers.Adam(1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

for i in range(200):
    train(train_dataset, 100)
    images = generator(tf.random.normal([BATCH_SIZE, latent_dimension]))

    print(np.amax(images[0]))
    plt.imshow((np.array(images[0]) * 12).astype(int))
    plt.show()
