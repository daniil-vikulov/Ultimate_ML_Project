import tensorflow as tf
import numpy as np
from keras.preprocessing import image
from keras.applications import imagenet_utils
import os


def load_images_from_directory(directory):
    files = os.listdir(directory)

    jpg_files = [f for f in files if f.lower().endswith('.jpg')]

    image_list = []
    for file in jpg_files:
        image_path = os.path.join(directory, file)

        img = image.load_img(image_path, target_size=(224, 224))

        img_array = image.img_to_array(img)

        final_image = np.expand_dims(img_array, axis=0)
        final_image = tf.keras.applications.mobilenet.preprocess_input(final_image)

        image_list.append(final_image)

    return image_list


images = load_images_from_directory(
    '/mnt/c/Users/dv/PycharmProjects/Ultimate_ML_Project/backend/data/train/non-erotic/')

mobile = tf.keras.applications.mobilenet_v2.MobileNetV2()

for image in images:
    prediction = mobile.predict(image)
    result = imagenet_utils.decode_predictions(prediction)
    print(result)
