from pathlib import Path
from typing import Any
import json

def write_to_json_file(file: Path, json_data: Any) -> None:
        
        file.parent.mkdir(parents=True, exist_ok=True)
        file.touch(exist_ok=True)

        with file.open("w") as f:
            json.dump(json_data,f,indent=4)

def read_json_file(file: Path):
        
    json_data = None
    with file.open() as f:
        json_data = json.load(f)
    return json_data