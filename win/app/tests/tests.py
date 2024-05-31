from win.app.back.model_wrapper import Detector
from windows_capture import WindowsCapture, Frame, InternalCaptureControl

import win32gui
from win.app.back.capturer import Capturer

import time


def test_model_categories():
    print()
    for tolerance in range(0, 4):
        for no_face in [False, True]:
            print(
                f'Tolerance: {tolerance}, No Face: {no_face}\n\t{Detector.__generate_categories__(tolerance, no_face)}\n')


capture = WindowsCapture(
    cursor_capture=False, draw_border=False, monitor_index=1, window_name="Settings")


@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    frame.save_as_image("image.png")

    capture_control.stop()


@capture.event
def on_closed():
    print("Capture Session Closed")


def enum_windows_proc(hwnd, hwnd_list):
    """Callback function to handle window enumeration."""
    if win32gui.IsWindowVisible(hwnd):
        hwnd_list.append((hwnd, win32gui.GetWindowText(hwnd)))


def get_visible_windows():
    """Retrieve a list of all visible windows with their hierarchy."""
    hwnd_list = []
    win32gui.EnumWindows(enum_windows_proc, hwnd_list)
    sorted_hwnd_list = sorted(hwnd_list, key=lambda x: win32gui.GetWindowRect(x[0]))
    return sorted_hwnd_list


def test_prints_windows():
    print()
    windows = get_visible_windows()
    for hwnd, title in windows:
        print(f"HWND: {hwnd}, Title: {title}")


def test_capturer():
    print()
    Capturer.__clear__()
    windows = Capturer.__list_windows__()
    print(windows)
    for window, title in windows:
        print("Capturing window: " + title)
        t = time.time()
        capturer = Capturer()
        capturer.__capture_window__(title)
        print(time.time() - t)


def test_advanced_screenshot():
    capturer = Capturer()
    image = capturer.get_screenshot()
    image.save("screenshot.png")


test_advanced_screenshot()
# test_capturer()
# capturer = Capturer()
# capturer.__capture_window__(title)
