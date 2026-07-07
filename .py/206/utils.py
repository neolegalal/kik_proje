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

def read_text(path):
    path = Path(path)
    if not path.exists():
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")
        except Exception:
            pass
    return ""

def write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def backup_file(path, backup_dir):
    path = Path(path)
    if not path.exists():
        return None
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()
    backup_path = backup_dir / f"{path.name}.{stamp}.bak"
    shutil.copy2(path, backup_path)
    return str(backup_path)

def file_status(path):
    path = Path(path)
    if not path.exists():
        return {"exists": False, "size": 0, "path": str(path)}
    return {"exists": True, "size": path.stat().st_size, "path": str(path)}
