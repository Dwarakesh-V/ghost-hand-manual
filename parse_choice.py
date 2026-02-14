import time
import tkinter as tk
import re
import subprocess

import sys
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from pynput.mouse import Controller, Button

def draw_phantom_box(coords):
    target_x, target_y = int(coords[0]), int(coords[1])

    if not tk._default_root:
        root = tk.Tk()
        root.withdraw()

    # Create the window
    arrow = tk.Toplevel()
    arrow.overrideredirect(True)
    arrow.wm_attributes("-topmost", True)

    w, h = 20, 20
    win_x = int(target_x)
    win_y = int(target_y)+10
    arrow.geometry(f"{w}x{h}+{win_x}+{win_y}")

    bg_color = 'white'
    arrow.configure(bg=bg_color)

    canvas = tk.Canvas(arrow, width=w, height=h, bg=bg_color, highlightthickness=0)
    canvas.pack()

    points = [
        w / 2, 4,   # Tip (Top Center)
        w-4, h-4,       # Bottom Right
        4, h-4        # Bottom Left
    ]
    canvas.create_polygon(points, fill='red', outline='red')

    arrow.wait_visibility(arrow)
    arrow.attributes('-alpha', 0.2) 
    arrow.update()

def draw_phantom_text(content):
    cmd = [
        "yad",
        "--title=Explanation",
        "--text-info",
        "--no-buttons",
        "--wrap",
        "--fontname=Liberation Sans 10",
        "--borders=10",
        "--geometry=350x600-20+40",
    ]

    subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        text=True
    ).stdin.write(content)

app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)


def draw_arrow(num, loc):
    x,y = loc
    # Load arrow image
    img = Image.open("arrow.png").convert("RGBA")

    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()

    text = str(num)

    # center text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    iw, ih = img.size
    pos = ((iw - tw) // 2, (ih - th) // 2)

    draw.text(pos, text, fill="black", font=font)

    # Save temporary image
    temp_path = "_arrow_temp.png"
    img.save(temp_path)

    # Overlay window
    label = QLabel()
    pixmap = QPixmap(temp_path)

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
    label.show()

    app.exec_()

def click_at(coords):
    mouse = Controller()
    mouse.position = coords
    time.sleep(0.01)
    mouse.click(Button.left, 1)

def parse_choice(elements, choice):
    print(choice)
    time.sleep(0.5)

    # Find the ACTION line safely (last occurrence)
    matches = re.findall(r"ACTION:\s*choose\s+([0-9,\s]+)", choice, re.IGNORECASE)

    if not matches:
        matches = re.findall(r"ARROWS:\s*choose\s+([0-9,\s]+)", choice, re.IGNORECASE)
        choice = choice.strip()
        draw_phantom_text(choice[14:])
        indices_str = matches[-1]
        choices = [c.strip() for c in indices_str.split(",") if c.strip()]
        for i in choices:
            draw_arrow(i,elements[i]["location"])
        return

    # Use the last valid ACTION match
    indices_str = matches[-1]
    choices = [c.strip() for c in indices_str.split(",") if c.strip()]

    print(f"Choices: {choices}")

    original_mouse = Controller()
    original_loc = original_mouse.position

    for idx in choices:
        index = int(idx)
        loc = elements[index]["location"]
        print(elements[index], loc)
        draw_phantom_box(loc)
        time.sleep(0.02)

    original_mouse.position = original_loc