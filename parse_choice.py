import tkinter as tk

def draw_phantom_box(coords):
    target_x, target_y = int(coords[0]), int(coords[1])

    if not tk._default_root:
        root = tk.Tk()
        root.withdraw()

    # Create the window
    arrow = tk.Toplevel()
    arrow.overrideredirect(True)
    arrow.wm_attributes("-topmost", True)

    # 1. Geometry: Pointing straight up
    # We want the TIP of the triangle (w/2, 0) to be at target_x, target_y
    w, h = 20, 20
    win_x = int(target_x)
    win_y = int(target_y)+10
    arrow.geometry(f"{w}x{h}+{win_x}+{win_y}")

    # 2. The Color Fix
    # Since systemTransparent failed, we use 'black' and then 
    # make the whole window semi-transparent using alpha.
    bg_color = 'white'
    arrow.configure(bg=bg_color)

    # 3. Create Canvas
    # highlightthickness=0 is vital on Linux to remove the gray border
    canvas = tk.Canvas(arrow, width=w, height=h, bg=bg_color, highlightthickness=0)
    canvas.pack()

    # 4. Draw STRAIGHT triangle pointing UP
    # [Tip-X, Tip-Y, Bottom-Right-X, Bottom-Right-Y, Bottom-Left-X, Bottom-Left-Y]
    points = [
        w / 2, 4,   # Tip (Top Center)
        w-4, h-4,       # Bottom Right
        4, h-4        # Bottom Left
    ]
    canvas.create_polygon(points, fill='red', outline='red')

    arrow.wait_visibility(arrow)
    arrow.attributes('-alpha', 0.2) 
    arrow.update()

def parse_choice(elements,choice):
    inss = choice.split(maxsplit=1)
    if not inss[0].lower() == "choose":
        print(f"Model response cannot be parsed. {choice}")
        return None
    else:
        choices = inss[1].split(",")
        for idx in choices:
            index = int(idx.strip())
            loc = elements[index]["location"]
            draw_phantom_box(loc)