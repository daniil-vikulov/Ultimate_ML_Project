from PyQt5 import QtCore

from win.app.back.background_task import LoopThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QSystemTrayIcon, QMenu, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QFont

from win.app.tools import calculate_font_size


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tray_icon = None
        self.button = None
        self.lay = None
        self.icon = QIcon('data/icon.png')
        self.initUI()
        self.thread = LoopThread()
        self.thread.start()

    def initUI(self):
        self.setWindowTitle('BabyGuard')
        self.setGeometry(300, 300, 400, 300)
        self.setWindowIcon(self.icon)

        self.add_widgets()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.icon)

        quit_action = QMenu("Exit")
        quit_action.addAction("Exit", QApplication.instance().quit)
        self.tray_icon.setContextMenu(quit_action)

        self.tray_icon.show()

    def add_widgets(self):
        central_widget = QWidget(self)

        self.setCentralWidget(central_widget)

        self.button = QPushButton('Start', self)
        self.button.clicked.connect(self.button_handler)
        self.button.setFont(QFont('Arial', calculate_font_size()))
        self.button.adjustSize()

        self.lay = QVBoxLayout(central_widget)
        self.lay.setAlignment(QtCore.Qt.AlignCenter)
        self.lay.addWidget(self.button)

    def button_handler(self):
        if self.button.text() == 'Start':
            self.button.setText('Stop')
            self.button.adjustSize()
            self.thread.start_loop()
        else:
            self.button.setText('Start')
            self.button.adjustSize()
            self.thread.stop_loop()

    def closeEvent(self, event):
        if self.button.text() == 'Stop':
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "BabyGuard",
                "The application is still running in the background.",
                QSystemTrayIcon.Information, 2000)
        else:
            print("terminating")
            event.accept()
