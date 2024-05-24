from PyQt5.QtCore import QThread, pyqtSignal


class LoopThread(QThread):
    run_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        while True:
            if self.running:
                self.looptick()

    def looptick(self):
        # TODO add real logic
        print("Tick")

    def start_loop(self):
        self.running = True

    def stop_loop(self):
        self.running = False
