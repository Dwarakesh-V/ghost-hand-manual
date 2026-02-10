import time
import tkinter as tk
import re
import subprocess

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

def draw_phantom_text(content, pos):
    x, y = pos

    cmd = [
        "yad",
        "--text-info",
        "--no-buttons",
        f"--geometry=+{x}+{y}",
        "--width=1",
        "--height=1"
    ]

    subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        text=True
    ).stdin.write(content)


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
        all_choices = choice.split("\n")
        for c in all_choices:
            idxc,content = c.split(maxsplit=1)
            locb = elements[idxc]["location"]
            draw_phantom_text(content,locb)

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
        click_at(loc)
        time.sleep(0.02)

    original_mouse.position = original_loc