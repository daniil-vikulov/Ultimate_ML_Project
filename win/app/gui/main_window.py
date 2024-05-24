from win.app.back.background_task import LoopThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tray_icon = None
        self.button = None
        self.icon = QIcon("C:\\Users\\dv\\PycharmProjects\\Ultimate_ML_Project\\win\\app\\data\\icon.png")
        self.initUI()
        self.thread = LoopThread()
        self.thread.start()

    def initUI(self):
        self.setWindowTitle('BabyGuard')
        self.setGeometry(300, 300, 200, 100)
        self.setWindowIcon(self.icon)

        self.button = QPushButton('Start', self)
        # noinspection PyUnresolvedReferences
        self.button.clicked.connect(self.button_handler)
        self.button.resize(self.button.sizeHint())
        self.button.move(50, 30)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.icon)

        quit_action = QMenu("Exit")
        quit_action.addAction("Exit", QApplication.instance().quit)
        self.tray_icon.setContextMenu(quit_action)

        self.tray_icon.show()

    def button_handler(self):
        if self.button.text() == 'Start':
            self.button.setText('Stop')
            self.thread.start_loop()
        else:
            self.button.setText('Start')
            self.thread.stop_loop()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Running in the background",
            "The application is still running in the background.",
            QSystemTrayIcon.Information,
            2000
        )
