import time
import re
import sys

from PIL import Image, ImageDraw, ImageFont
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QTextEdit, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPolygon, QColor, QFont
from PyQt5.QtCore import Qt, QPoint

from pynput.mouse import Controller, Button


app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

OVERLAYS = []


class PhantomBox(QWidget):
    def __init__(self, x, y):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(x, y + 10, 20, 20)
        self.setWindowOpacity(0.2)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor("red"))
        painter.setPen(QColor("red"))
        painter.drawPolygon(QPolygon([
            QPoint(10, 4),
            QPoint(16, 16),
            QPoint(4, 16)
        ]))


def draw_phantom_box(coords):
    x, y = int(coords[0]), int(coords[1])
    box = PhantomBox(x, y)
    OVERLAYS.append(box)
    box.show()


class PhantomText(QWidget):
    def __init__(self, content):
        super().__init__()
        self.setWindowTitle("Explanation")
        self.setGeometry(1800, 100, 700, 1250)

        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)

        font = QFont("Liberation Sans", 22)
        font.setBold(True)
        text.setFont(font)

        text.setText(content)

        layout.addWidget(text)
        self.setLayout(layout)

def draw_phantom_text(content):
    w = PhantomText(content)
    OVERLAYS.append(w)
    w.show()

def draw_arrow(num, loc):
    x, y = loc

    img = Image.open("arrow.png").convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Bigger font
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    except:
        font = ImageFont.load_default()

    text = str(num)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    iw, ih = img.size

    padding_x = 10
    padding_y = 10

    box_w = tw + padding_x * 2
    box_h = th + padding_y * 2

    bx = (iw - box_w) // 1.5
    by = (ih - box_h)

    # Rounded black background
    draw.rounded_rectangle(
        [bx, by, bx + box_w, by + box_h],
        radius=999,
        fill="black"
    )

    # White text
    draw.text(
        (bx + box_w // 2, by + box_h // 2),
        text,
        # fill="#ff6d00",
        fill = "#ffffff",
        font=font,
        anchor="mm"   # center-middle anchor
    )

    qim = ImageQt(img)
    pixmap = QPixmap.fromImage(qim)

    label = QLabel()
    label.setPixmap(pixmap)
    label.resize(pixmap.width(), pixmap.height())

    label.setWindowFlags(
        Qt.FramelessWindowHint |
        Qt.WindowStaysOnTopHint |
        Qt.Tool
    )

    label.setAttribute(Qt.WA_TranslucentBackground)
    label.setStyleSheet("background: transparent;")
    label.move(x, y)

    OVERLAYS.append(label)
    label.show()

def click_at(coords):
    mouse = Controller()
    mouse.position = coords
    time.sleep(0.01)
    mouse.click(Button.left, 1)


def parse_choice(elements, choice):
    matches = re.findall(r"ACTION:\s*choose\s+([0-9,\s]+)", choice, re.IGNORECASE)

    if not matches:
        draw_phantom_text(choice[14:])

        matches = re.findall(r"ARROWS:\s*([0-9,\s]+)", choice, re.IGNORECASE)
        if matches:
            indices_str = matches[-1]
            choices = [c.strip() for c in indices_str.split(",") if c.strip()]
            for i in choices:
                print("DEBUG:",elements[int(i)])
                draw_arrow(int(i), elements[int(i)]["location"])
        return

    indices_str = matches[-1]
    choices = [c.strip() for c in indices_str.split(",") if c.strip()]

    original_mouse = Controller()
    original_loc = original_mouse.position

    for idx in choices:
        index = int(idx)
        loc = elements[index]["location"]
        draw_phantom_box(loc)
        time.sleep(0.02)

    original_mouse.position = original_loc
