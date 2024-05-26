import math
import ctypes


def get_screen_resolution():
    """
    Returns a pair of integers: screen's width and height
    """

    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    return width, height


def calculate_font_size():
    """
    Calculate font size based on screen resolution

    Returns:
    int: ideal size
    """

    width, height = get_screen_resolution()

    len_px = math.sqrt(width ** 2 + height ** 2)
    full_hd_len_px = math.sqrt(1920 ** 2 + 1080 ** 2)

    return int(round((len_px / full_hd_len_px) * 16))
