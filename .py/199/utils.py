# -*- coding: utf-8 -*-
import json, shutil
from pathlib import Path
from datetime import datetime

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_dirs(*dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def disk_free_gb(path):
    usage = shutil.disk_usage(str(path))
    return round(usage.free / (1024 ** 3), 2)

def safe_read(path, limit_chars=500000):
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

def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def latest_file(folder, pattern):
    folder = Path(folder)
    if not folder.exists():
        return None
    files = list(folder.glob(pattern))
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]

def find_scripts(py_dir, prefix, must_contain=None):
    must_contain = must_contain or []
    py_dir = Path(py_dir)
    candidates = []
    candidates.extend(py_dir.glob(f"{prefix}*.py"))
    candidates.extend(py_dir.glob(f"*{prefix}*.py"))
    candidates = list(set(candidates))
    if must_contain:
        candidates = [p for p in candidates if all(t.lower() in p.name.lower() for t in must_contain)]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates

def file_info(path):
    path = Path(path)
    return {
        "path": str(path),
        "name": path.name,
        "size_kb": round(path.stat().st_size / 1024, 2),
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
    }
