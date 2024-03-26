import cv2
import os
from nudenet import NudeDetector
from colours import colours


def censor_colour(image_path, colour, classes=None, output_path=None):
    if classes is None:
        classes = []
    nd = NudeDetector()
    detections = nd.detect(image_path)
    face_classes = ['FACE_FEMALE', 'FACE_MALE']
    only_face_classes = all(detection["class"] in face_classes for detection in detections)
    if classes:
        detections = [
            detection for detection in detections if detection["class"] in classes
        ]

    img = cv2.imread(image_path)

    for detection in detections:
        c = detection["class"]
        box = detection["box"]
        x, y, w, h = box[0], box[1], box[2], box[3]
        if not only_face_classes or c not in face_classes:
            img[y: y + h, x: x + w] = colours[colour]

    if not output_path:
        image_path, ext = os.path.splitext(image_path)
        output_path = f"{image_path}_censored{ext}"

    cv2.imwrite(output_path, img)

    return output_path


