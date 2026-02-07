# Custom
from at_spi_tree import *
from box_coords import get_box_coords
from gemini_api_gen import generate_text
from para_maker import at_pm
from parse_choice import parse_choice

# Built-in
import time

def run_model(mode):
    screen_loc = get_box_coords()
    print(screen_loc)
    time.sleep(1) # To ensure focus returns to the actual app instead of tkinter app
    cur_app = find_application_by_pid(get_focused_window_pid())
    cur_app_tree = traverse_tree(cur_app)
    cur_app_selected = []
    for element in cur_app_tree:
        # element["location"][0] -> element x, element["location"][1] -> element y
        # screen_loc[0] -> min(x), screen_loc[2] -> max(x), screen_loc[1] -> min(y), screen_loc[3] -> max(y)
        if element["location"][0] >= screen_loc[0] and element["location"][0] <= screen_loc[2]:
            if element["location"][1] >= screen_loc[1] and element["location"][1] <= screen_loc[3]:
                cur_app_selected.append(element)

    cur_app_data = at_pm(cur_app_selected)

    if mode == "answer":
        with open("ans_ins.txt") as f:
            ins = f.read()
    else:
        with open("expl_ins.txt") as f:
            ins = f.read()

    prompt = f"System: {ins}\n\nTree:\n{cur_app_data}"
    # print(prompt) # Debug log
    return (cur_app_selected,generate_text(prompt))

    # Debug returns
    # return (cur_app_selected,"choose 4")
    # return (cur_app_selected,"choose 6,18,30,33")

if __name__ == "__main__":
    time.sleep(1)
    final = run_model("answer")
    parse_choice(final[0],final[1])
    time.sleep(10)