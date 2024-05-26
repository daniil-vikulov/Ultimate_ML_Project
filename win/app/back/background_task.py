from PyQt5.QtCore import QThread, pyqtSignal

from PIL import ImageGrab



class LoopThread(QThread):
    run_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = False
        self.detector = NudeDetector()

    def run(self):
        while True:
            if self.running:
                self.looptick()

    def looptick(self):
        screenshot = ImageGrab.grab()
        screenshot.save('screenshot.png')
        result = self.detector.detect(image_path='screenshot.png')
        print(result)

    def start_loop(self):
        self.running = True

    def stop_loop(self):
        self.running = False
