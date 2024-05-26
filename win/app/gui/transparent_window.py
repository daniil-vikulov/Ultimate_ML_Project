from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter


class TransparentWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle('BabyGuard canvas')
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.rectangles = []

    def set_rectangle(self, rectangles):
        self.rectangles = rectangles
        self.repaint()

    def paintEvent(self, event):
        print("Redrawing...", len(self.rectangles))
        painter = QPainter(self)
        painter.setBrush(QtGui.QColor(255, 0, 0))
        painter.setPen(QtCore.Qt.NoPen)

        # painter.drawRect(200, 200, 300, 300)

        for rect in self.rectangles:
            painter.drawRect(rect[0], rect[1], rect[2], rect[3])
