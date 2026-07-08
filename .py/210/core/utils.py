# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_dirs(*dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def safe_json(path):
    path = Path(path)
    if not path.exists():
        return {}
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return json.loads(path.read_text(encoding=enc, errors="ignore"))
        except Exception:
            pass
    return {}

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_jsonl(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
