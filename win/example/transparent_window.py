import sys
from PyQt5 import QtWidgets, QtGui, QtCore


class TransparentWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('Transparent Window with Solid Rectangle')
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QColor(255, 0, 0))

        painter.setPen(QtCore.Qt.NoPen)

        painter.drawRect(300, 300, 300, 300)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = TransparentWindow()
    win.showFullScreen()
    sys.exit(app.exec_())
