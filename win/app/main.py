import sys

from PyQt5.QtWidgets import QApplication

from win.app.gui.main_window import MainWindow, TransparentWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
