import json

def get_json_from_file(file_path: str) -> dict:
    with open(file_path, "r") as json_file:
        data = json.loads(json_file.read())
    
    return data
