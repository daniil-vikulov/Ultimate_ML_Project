from PIL import ImageGrab
from PyQt5.QtCore import QThread, pyqtSignal
from win.app.back.model_wrapper import Detector


class LoopThread(QThread):
    run_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = False
        self.detector = Detector(0, False)

    def run(self):
        while True:
            if self.running:
                self.loop_tick()

    def loop_tick(self):
        screenshot = ImageGrab.grab()
        screenshot.save('screenshot.png')
        result = self.detector.censor(screenshot)
        print(result)

    def start_loop(self):
        self.running = True

    def stop_loop(self):
        self.running = False
