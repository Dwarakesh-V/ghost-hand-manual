import time
import tkinter as tk

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

def draw_phantom_text(text):
    if not tk._default_root:
        root = tk.Tk()
        root.withdraw()

    panel = tk.Toplevel()
    # panel.overrideredirect(True)
    panel.wm_attributes("-topmost", True)

    bg_color = "white"
    panel.configure(bg=bg_color)

    # Screen dimensions
    screen_w = panel.winfo_screenwidth()
    screen_h = panel.winfo_screenheight()

    margin_x = 30
    margin_y = 200
    panel_width = 1000

    label = tk.Label(
        panel,
        text=text,
        fg="black",
        bg=bg_color,
        font=("Liberation sans", 12),
        justify="left",
        wraplength=panel_width - 20
    )
    label.pack(padx=10, pady=10)

    panel.update_idletasks()
    panel_height = panel.winfo_height()

    # Right-side placement (Copilot-style)
    x = screen_w - panel_width - margin_x
    y = margin_y

    panel.geometry(f"{panel_width}x{panel_height}+{x}+{y}")

    panel.wait_visibility(panel)
    panel.update()

    return panel

def click_at(coords):
    mouse = Controller()
    mouse.position = coords
    time.sleep(0.01)
    mouse.click(Button.left, 1)

def parse_choice(elements,choice):
    print(choice)
    time.sleep(0.5)
    inss = choice.split(maxsplit=1)
    if inss[0].lower() == "choose":
        choices = inss[1].split(",")
        print(f"Choices: {choices}")
        original_mouse = Controller()
        original_loc = original_mouse.position
        for idx in choices:
            index = int(idx.strip())
            loc = elements[index]["location"]
            print(elements[index],elements[index]["location"])
            click_at(loc) # Buffer to focus inside the element instead of exactly at the topleft corner
        original_mouse.position = original_loc
    else:
        draw_phantom_text(choice)