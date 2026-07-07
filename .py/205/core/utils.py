# -*- coding: utf-8 -*-
import json
import shutil
from pathlib import Path
from datetime import datetime

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_dirs(*dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def safe_read(path, limit_chars=5000000):
    path = Path(path)
    if not path.exists():
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")[:limit_chars]
        except Exception:
            pass
    return ""

def safe_json(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None

def read_jsonl(path):
    path = Path(path)
    rows = []
    invalid = 0
    if not path.exists():
        return rows, invalid
    for line in safe_read(path).splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            invalid += 1
    return rows, invalid

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def append_jsonl(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def disk_free_gb(path):
    usage = shutil.disk_usage(str(path))
    return round(usage.free / (1024 ** 3), 2)

def clamp(value, min_value=0, max_value=100):
    try:
        value = float(value)
    except Exception:
        value = 0
    return max(min_value, min(max_value, value))
