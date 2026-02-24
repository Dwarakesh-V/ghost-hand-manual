import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect
import json
from pathlib import Path
BASE_DIR = Path(__file__).parent

class SelectionOverlay(QWidget):
    def __init__(self, opacity=0.05):
        super().__init__()

        self.start = None
        self.end = None
        self.selection = None
        self.opacity = opacity

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_X11DoNotAcceptFocus)

        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(255 * self.opacity)))

        if self.start and self.end:
            pen = QPen(QColor(255, 255, 255, int(self.opacity*255)))
            pen.setWidth(2)
            painter.setPen(pen)
            rect = QRect(self.start, self.end)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        rect = QRect(self.start, event.pos()).normalized()
        x, y, w, h = rect.getRect()
        self.selection = (x, y, x + w, y + h)
        QApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.selection = None
            QApplication.quit()


def get_box_coords():
    with open(f"{BASE_DIR}/instructions.json") as f:
        ins = json.load(f)
        stealth = ins["stealth"]
        stealth = max(0, min(0.95, stealth))
        opacity=1-stealth
    app = QApplication.instance()
    owns_app = False

    if app is None:
        app = QApplication(sys.argv)
        owns_app = True

    overlay = SelectionOverlay(opacity=opacity)
    overlay.show()

    app.exec()

    result = overlay.selection

    if owns_app:
        app.quit()

    return result

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = SelectionOverlay(opacity=0.1)
    overlay.show()
    sys.exit(app.exec())