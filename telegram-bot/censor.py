import cv2
import os
from nudenet import NudeDetector


def censor_black(image_path, classes=None, output_path=None):
    if classes is None:
        classes = []
    nd = NudeDetector()
    detections = nd.detect(image_path)
    if classes:
        detections = [
            detection for detection in detections if detection["class"] in classes
        ]

    img = cv2.imread(image_path)

    for detection in detections:
        box = detection["box"]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # change these pixels to pure black
        img[y: y + h, x: x + w] = (0, 0, 0)

    if not output_path:
        image_path, ext = os.path.splitext(image_path)
        output_path = f"{image_path}_censored{ext}"

    cv2.imwrite(output_path, img)

    return output_path


def censor_blue(image_path, classes=None, output_path=None):
    if classes is None:
        classes = []
    nd = NudeDetector()
    detections = nd.detect(image_path)
    if classes:
        detections = [
            detection for detection in detections if detection["class"] in classes
        ]

    img = cv2.imread(image_path)

    for detection in detections:
        box = detection["box"]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # change these pixels to blue
        img[y: y + h, x: x + w] = (255, 0, 0)

    if not output_path:
        image_path, ext = os.path.splitext(image_path)
        output_path = f"{image_path}_censored{ext}"

    cv2.imwrite(output_path, img)

    return output_path
