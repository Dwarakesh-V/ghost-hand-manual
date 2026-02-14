import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

app = QApplication(sys.argv)

label = QLabel()
pixmap = QPixmap("arrow.png")

if pixmap.isNull():
    print("Failed to load image")
    sys.exit()

label.setPixmap(pixmap)
label.resize(pixmap.width(), pixmap.height())

label.setWindowFlags(
    Qt.FramelessWindowHint |
    Qt.WindowStaysOnTopHint |
    Qt.Tool
)

label.move(400, 200)
label.setAttribute(Qt.WA_TranslucentBackground)
label.setStyleSheet("background: transparent;")
label.show()

sys.exit(app.exec_())
