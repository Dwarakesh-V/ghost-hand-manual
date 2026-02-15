# Custom
from at_spi_tree import *
from box_coords import get_box_coords
from gemini_api_gen import generate_gemini_text
from para_maker import at_pm
from parse_choice import parse_choice
from web_aut import rcv_web_int

# Built-in
import time
import json
from pathlib import Path
import asyncio
import sys

from PyQt5.QtWidgets import QApplication

BASE_DIR = Path(__file__).parent

def generate_llama_text(model,tokenizer,messages):
    """Generate a response from the model"""
    # Apply chat template
    import torch # On demand import
    prompt = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            do_sample=False,
            # temperature=0.4,
            pad_token_id=tokenizer.eos_token_id
        )
    
    # Decode only the new tokens
    response = tokenizer.decode(
        outputs[0][inputs['input_ids'].shape[1]:], 
        skip_special_tokens=True
    )
    
    return response

def run_model():
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

    with open(f"{BASE_DIR}/instructions.json") as f:
        ins = json.load(f)
        mode = ins["mode"]
        model_type = ins["model_type"]
        web_model = ins["web_model"]

    if mode == "answer":
        with open(f"{BASE_DIR}/ans_ins.txt") as f:
            ins = f.read()
    else:
        with open(f"{BASE_DIR}/expl_ins.txt") as f:
            ins = f.read()
    
    if model_type == "api":
        prompt = f"System: {ins}\n\nTree:\n{cur_app_data}"
        return (cur_app_selected,generate_gemini_text(prompt))
    
    elif model_type == "local":
        # Download
        # Import on demand
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        # Load model on demand
        model_path = f"{BASE_DIR}/Llama-3.1-8B-Instruct"

        # Define the quantization configuration
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        ) # Quantize to 4 bit int

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quant_config, # uncomment to quantize larger models
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        messages = [
            {
                "role": "system",
                "content": ins
            },
            {
                "role": "user",
                "content": f"Tree:\n{cur_app_data}"
            }
        ]
        print(cur_app_data)

        return (cur_app_selected,generate_llama_text(model,tokenizer,messages))
    
    elif model_type == "web":
        # model_response = asyncio.run(rcv_web_int(web_model,cur_app_data))
        # return (cur_app_selected,model_response)
        return (cur_app_selected,"txt\nCopy code\nDo something\nARROWS: 1,2,3,4,5,6")
        
    else:
        return (cur_app_selected,"choose 6,18,30,33") # Debug

if __name__ == "__main__":    
    time.sleep(1)
    final = run_model()
    app = QApplication(sys.argv)
    parse_choice(final[0],final[1])
    app.exec_()