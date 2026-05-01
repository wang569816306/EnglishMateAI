# app/core/prompt_loader.py
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_prompt(scene: str = "english_teacher"):
    path = os.path.join(BASE_DIR, "prompts", f"{scene}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["system_prompt"]