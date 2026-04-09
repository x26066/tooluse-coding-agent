import json
from datetime import datetime
from pathlib import Path


def save_log(log_dir: Path, data: dict):
    log_dir.mkdir(parents=True, exist_ok=True)
    file_path = log_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path


def save_named_json(file_path: Path, data: dict):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path