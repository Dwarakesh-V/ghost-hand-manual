import tkinter as tk
import sys
import time
import json

from pathlib import Path
BASE_DIR = Path(__file__).parent

def get_box_coords():
    """
    Creates a full-screen transparent overlay allowing the user to draw 
    a selection box. Captures immediately on mouse release.
    """
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    
    transparent_bg = 'black' # Black overlay color

    # Transparency settings
    root.wait_visibility(root)
    root.configure(background=transparent_bg)
    with open(f"{BASE_DIR}/instructions.json") as f:
        ins = json.load(f)
        stealth = ins["stealth"]
        # Hard caps
        stealth = max(0,stealth)
        stealth = min(1,stealth)
        stealth = 0.55-(0.05 + stealth*0.45)
    root.wm_attributes("-alpha", stealth) # Between 0.05 and 0.5

    # Create canvas with the transparent background color
    # canvas = tk.Canvas(root, cursor="cross", bg=transparent_bg, highlightthickness=0)
    canvas = tk.Canvas(root, bg=transparent_bg, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # State variables
    start_x = None
    start_y = None
    rect_id = None
    selection_coords = None

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect_id
        start_x = event.x
        start_y = event.y
        
        if rect_id:
            canvas.delete(rect_id)
        
        # Draw the box in White
        rect_id = canvas.create_rectangle(
            start_x, start_y, start_x, start_y, 
            outline='white', 
            width=2
        )

    def on_mouse_drag(event):
        nonlocal rect_id
        if rect_id:
            canvas.coords(rect_id, start_x, start_y, event.x, event.y)

    def on_mouse_release(event):
        nonlocal selection_coords
        
        if rect_id:
            coords = canvas.coords(rect_id)
            x1, y1, x2, y2 = coords
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            if right - left > 5 and bottom - top > 5: # Minimum threshold
                selection_coords = (int(left), int(top), int(right), int(bottom))
                
                # Cleanup and close
                root.withdraw()
                root.update_idletasks()
                time.sleep(0.1)
                root.quit()
                root.destroy()
            else:
                pass

    def on_escape_press(event):
        root.destroy()
        sys.exit("Selection cancelled.")

    canvas.bind('<Button-1>', on_mouse_down)
    canvas.bind('<B1-Motion>', on_mouse_drag)
    canvas.bind('<ButtonRelease-1>', on_mouse_release)
    root.bind('<Escape>', on_escape_press)

    root.mainloop()
    
    return selection_coords


if __name__ == "__main__":
    time.sleep(1)
    try:
        coords = get_box_coords()
        if coords:
            print(f"Captured Area: {coords}")
    except Exception as e:
        print(f"Error: {e}")