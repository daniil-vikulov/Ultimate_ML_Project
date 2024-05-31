from PIL import ImageGrab
from PyQt5.QtCore import QThread, pyqtSignal
from win.app.back.model_wrapper import Detector

from win.app.back.capturer import Capturer


class LoopThread(QThread):
    run_signal = pyqtSignal(bool)
    update_canvas_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.running = False
        self.detector = Detector(1, False)
        # self.prev_rectangles = []

    def run(self):
        while True:
            if self.running:
                self.loop_tick()

    def loop_tick(self):
        # rectangles = self.prev_rectangles
        # self.update_canvas_signal.emit([])
        capturer = Capturer()
        screenshot = capturer.get_screenshot()
        if screenshot is not None:
            # self.update_canvas_signal.emit(rectangles)
            result = self.detector.censor(screenshot)
            self.update_canvas_signal.emit(result)
            # self.prev_rectangles = result
            print(result)

    def start_loop(self):
        self.running = True

    def stop_loop(self):
        self.running = False
