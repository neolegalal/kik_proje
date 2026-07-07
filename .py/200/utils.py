# -*- coding: utf-8 -*-
import json
import shutil
import subprocess
import sys
import time
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

def run_command(command, cwd, timeout=600):
    started = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout,
        )
        return {
            "executed": True,
            "timeout": False,
            "returncode": proc.returncode,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": proc.stdout[-12000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-12000:] if proc.stderr else "",
            "status": "PASS" if proc.returncode == 0 else "FAIL",
        }
    except subprocess.TimeoutExpired as e:
        return {
            "executed": True,
            "timeout": True,
            "returncode": None,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": (e.stdout or "")[-12000:] if isinstance(e.stdout, str) else "",
            "stderr_tail": (e.stderr or "")[-12000:] if isinstance(e.stderr, str) else "",
            "status": "TIMEOUT",
        }
    except Exception as e:
        return {
            "executed": True,
            "timeout": False,
            "returncode": None,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": "",
            "stderr_tail": str(e),
            "status": "FAIL",
        }
