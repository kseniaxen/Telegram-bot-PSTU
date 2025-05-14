import json

def load_texts(file_path="text.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)