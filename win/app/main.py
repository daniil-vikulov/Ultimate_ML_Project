import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
import datetime
from image_util import is_safe


class ScreenshotApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Screenshot App")
        self.setGeometry(200, 200, 400, 200)

        self.button = QPushButton("Start", self)
        self.button.setGeometry(50, 30, 100, 40)
        self.button.clicked.connect(self.start_screenshots)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.take_screenshot)

    def start_screenshots(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText("Start")
        else:
            self.timer.start(1000)
            self.button.setText("Stop")

    @staticmethod
    def take_screenshot():
        screen = QApplication.primaryScreen()
        if screen:
            screenshot = screen.grabWindow(0)
            if not is_safe(screenshot):
                print("Saving unsafe screenshot...")
                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                filename = f"screenshot_{timestamp}.png"
                screenshot.save(filename, 'PNG')
                print(f"Saved: {filename}")


def main():
    app = QApplication(sys.argv)
    window = ScreenshotApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
