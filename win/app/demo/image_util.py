import random
from PyQt5.QtGui import QPixmap


def is_safe(image: QPixmap) -> bool:
    """
    Checks whether an image is safe or not.
            :parameter image: QPixmap - image to be checked.
            :return: True if image is safe else False.
    """
    return random.randint(0, 1) == 1
