import os

import pywintypes
import win32con
import win32gui
from PIL import Image
from windows_capture import WindowsCapture, Frame, InternalCaptureControl


class Capturer:
    banned_list = ['Windows Input Experience', 'NVIDIA GeForce Overlay', 'Settings', 'Program Manager',
                   'BabyGuard canvas']

    def __init__(self):
        pass

    def get_screenshot(self):
        Capturer.__clear__()
        windows_list = Capturer.__list_windows__()
        for window in windows_list:
            print(window[1])
            Capturer.__capture_window__(window[1])

        images = self.__get_screenshot_list__()
        ans = Capturer.__merge_images__(images, windows_list)
        Capturer.__clear__()

        return ans

    @staticmethod
    def __list_windows__():
        """Returns a list of (window descriptor, window title) of all windows, which should be capturer"""
        hwnd_list = []
        win32gui.EnumWindows(Capturer.__enum_windows_proc__, hwnd_list)
        res_list = Capturer.__filter_windows__([item for item in hwnd_list if item[1]])

        return Capturer.__sort_windows__(res_list)

    @staticmethod
    def __filter_windows__(windows):
        res = []
        for window in windows:
            rect = win32gui.GetWindowRect(window[0])
            if window[1] not in Capturer.banned_list:
                if rect[2] - rect[0] > 50 and rect[3] - rect[1] > 50:
                    res.append(window)

        return res

    @staticmethod
    def __enum_windows_proc__(hwnd, hwnd_list):
        """Callback function to handle window enumeration."""
        if win32gui.IsWindowVisible(hwnd):
            hwnd_list.append((hwnd, win32gui.GetWindowText(hwnd)))

    @staticmethod
    def __name_file__():
        i = 0
        while os.path.exists(f"{i}.bmp"):
            i += 1
        return f"{i}.bmp"

    @staticmethod
    def __capture_window__(window_name):
        print("Capturing...", window_name)
        capture = WindowsCapture(cursor_capture=False, draw_border=False, monitor_index=0, window_name=window_name)

        @capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            name = Capturer.__name_file__()
            print(name)
            frame.save_as_image(Capturer.__name_file__())

            capture_control.stop()

        @capture.event
        def on_closed():
            print(f"Capture Session for {window_name} Closed")

        # noinspection PyBroadException
        try:
            capture.start()
        except Exception:
            pass

    @staticmethod
    def __clear__():
        i = 0
        while True:
            file_name = f"{i}.bmp"
            if os.path.exists(file_name):
                os.remove(file_name)
                print(f"Removed {file_name}")
            else:
                break
            i += 1

    @staticmethod
    def __sort_windows__(windows):
        sorted_windows = []
        hwnd = win32gui.GetTopWindow(None)

        while hwnd:
            if hwnd in [window[0] for window in windows]:
                sorted_windows.append(hwnd)
            hwnd = win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)

        return [(hwnd, win32gui.GetWindowText(hwnd)) for hwnd in sorted_windows if win32gui.IsWindowVisible(hwnd)]

    @staticmethod
    def __get_screenshot_list__():
        images = []
        i = 0

        while True:
            file_name = f"{i}.bmp"
            if os.path.exists(file_name):
                try:
                    image = Image.open(file_name)
                    image.load()
                    images.append(image)
                except IOError:
                    print(f"Cannot load image: {file_name}")
            else:
                break
            i += 1

        return images

    @staticmethod
    def __merge_images__(images, windows):
        try:
            rects = [win32gui.GetWindowRect(hwnd) for hwnd, _ in windows]

            print(rects)

            max_right = max((rect[2]) for rect in rects)
            max_bottom = max((rect[3]) for rect in rects)

            print(max_right, max_bottom)

            final_image = Image.new("RGBA", (max_right, max_bottom), (0, 0, 0, 0))

            for img, rect in reversed(list(zip(images, rects))):
                if img.mode != 'RGBA':
                    print("Bad mod. Converting...")
                    img = img.convert('RGBA')
                left, top, right, bottom = rect
                final_image.paste(img, (left, top), img)
        except pywintypes.error as e:
            return None

        return final_image
