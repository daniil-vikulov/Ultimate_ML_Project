import cv2
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from keras.preprocessing import image
from keras.applications import imagenet_utils

# загружаем изображение
img = image.load_img('../data//train//non-erotic//3.jpg', target_size=(224, 224))

# используем модель MobileNetV2
mobile = tf.keras.applications.mobilenet_v2.MobileNetV2()
resized_img = image.img_to_array(img)
final_image = np.expand_dims(resized_img, axis=0)  # fourth dimension
final_image = tf.keras.applications.mobilenet.preprocess_input(final_image)
# print(final_image.shape)

# формируем предсказание насчет того, что изображено на картинке
prediction = mobile.predict(final_image)
result = imagenet_utils.decode_predictions(prediction)
print(result)
