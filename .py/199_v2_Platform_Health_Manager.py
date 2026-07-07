# -*- coding: utf-8 -*-
r"""
199 v2 - Platform Health Manager
NeoLegal Production Platform v2.0

Amaç:
- 199 v1 Service Registry çıktısını okumak.
- Platformun genel sağlığını tek merkezden değerlendirmek.
- DB, disk, queue, worker, recovery, certification ve service registry durumlarını özetlemek.
- Tek karar üretmek: PLATFORM READY / PLATFORM REVIEW / PLATFORM BLOCKED
- Production çalıştırmaz; yalnızca sağlık kontrolü yapar.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\199_v2_Platform_Health_Manager.py"
"""

import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
REGISTRY_PATH = STATE_DIR / "service_registry" / "199_service_registry.json"
QUEUE_FILE = STATE_DIR / "job_queue" / "198_job_queue_state.json"
WORKER_FILE = STATE_DIR / "job_queue" / "198_worker_state.json"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path, limit_chars=500000):
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")[:limit_chars]
        except Exception:
            pass
    return ""


def safe_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def latest_file(folder: Path, pattern: str):
    if not folder.exists():
        return None
    files = list(folder.glob(pattern))
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def discover_db():
    candidates = []
    for p in BASE_DIR.rglob("*.db"):
        if "kik" in p.name.lower():
            candidates.append(p)
    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not candidates:
        return {"status": "FAIL", "path": None, "table": None, "count": 0, "message": "KİK DB bulunamadı."}

    db_path = candidates[0]
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        table = None
        for t in ("hukuki_kartlar", "kararlar", "kik_kararlari", "cards", "legal_cards"):
            if t in tables:
                table = t
                break
        if not table and tables:
            table = tables[0]
        if not table:
            conn.close()
            return {"status": "FAIL", "path": str(db_path), "table": None, "count": 0, "message": "DB var ama tablo yok."}

        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return {"status": "PASS" if count > 0 else "WARNING", "path": str(db_path), "table": table, "count": count, "message": f"DB OK: {count}"}
    except Exception as e:
        return {"status": "FAIL", "path": str(db_path), "table": None, "count": 0, "message": f"DB okunamadı: {e}"}


def registry_health():
    reg = safe_json(REGISTRY_PATH)
    if not reg:
        return {"status": "FAIL", "found": 0, "total": 0, "message": "Service registry bulunamadı veya okunamadı."}

    flat = reg.get("flat_services", {})
    total = len(flat)
    found = sum(1 for item in flat.values() if item.get("status") == "FOUND")
    missing = [f"{k} {v.get('label')}" for k, v in flat.items() if v.get("status") != "FOUND"]

    status = "PASS" if total > 0 and found == total else ("WARNING" if found > 0 else "FAIL")
    return {"status": status, "found": found, "total": total, "missing": missing, "message": f"{found}/{total} servis bulundu."}


def queue_health():
    q = safe_json(QUEUE_FILE)
    if not q:
        return {"status": "WARNING", "message": "Queue dosyası yok veya okunamadı.", "total": 0}

    jobs = q.get("jobs", [])
    counts = {}
    for job in jobs:
        st = job.get("status", "UNKNOWN")
        counts[st] = counts.get(st, 0) + 1

    running = counts.get("RUNNING", 0)
    failed = counts.get("FAILED", 0)
    total = len(jobs)

    if total == 0:
        status = "WARNING"
    elif failed > 0:
        status = "WARNING"
    else:
        status = "PASS"

    return {
        "status": status,
        "total": total,
        "waiting": counts.get("WAITING", 0),
        "running": running,
        "finished": counts.get("FINISHED", 0),
        "failed": failed,
        "retry": counts.get("RETRY", 0),
        "counts": counts,
        "message": f"Queue total={total}, waiting={counts.get('WAITING',0)}, finished={counts.get('FINISHED',0)}"
    }


def worker_health():
    w = safe_json(WORKER_FILE)
    if not w:
        return {"status": "WARNING", "message": "Worker dosyası yok veya okunamadı.", "total": 0}

    workers = w.get("workers", [])
    counts = {}
    for worker in workers:
        st = worker.get("status", "UNKNOWN")
        counts[st] = counts.get(st, 0) + 1

    if not workers:
        status = "WARNING"
    elif counts.get("UNKNOWN", 0) > 0:
        status = "WARNING"
    else:
        status = "PASS"

    return {
        "status": status,
        "total": len(workers),
        "idle": counts.get("IDLE", 0),
        "running": counts.get("RUNNING", 0),
        "disabled": counts.get("DISABLED", 0),
        "counts": counts,
        "message": f"Workers total={len(workers)}, idle={counts.get('IDLE',0)}, running={counts.get('RUNNING',0)}"
    }


def latest_result_health(pattern, expected_tokens, label):
    f = latest_file(STATE_DIR, pattern)
    if not f:
        return {"status": "WARNING", "file": None, "message": f"{label} state bulunamadı."}

    text = safe_read(f).lower()
    ok = any(tok.lower() in text for tok in expected_tokens)

    return {
        "status": "PASS" if ok else "WARNING",
        "file": str(f),
        "message": f"{label}: {'OK' if ok else 'inceleme gerekli'}"
    }


def evaluate(parts):
    score = 100
    errors = []
    warnings = []

    weights = {
        "registry": 20,
        "db": 25,
        "disk": 15,
        "queue": 10,
        "worker": 10,
        "recovery": 10,
        "certification": 5,
        "dynamic": 5,
    }

    for key, weight in weights.items():
        item = parts.get(key, {})
        st = item.get("status")
        if st == "FAIL":
            score -= weight
            errors.append(f"{key} FAIL: {item.get('message')}")
        elif st == "WARNING":
            score -= max(2, weight // 2)
            warnings.append(f"{key} WARNING: {item.get('message')}")

    score = max(0, min(100, score))

    if errors:
        decision = "PLATFORM BLOCKED"
    elif score >= 90:
        decision = "PLATFORM READY"
    elif score >= 75:
        decision = "PLATFORM REVIEW"
    else:
        decision = "PLATFORM BLOCKED"

    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}


def write_outputs(payload):
    json_path = STATE_DIR / f"199_v2_platform_health_state_{NOW}.json"
    txt_path = REPORT_DIR / f"199_v2_platform_health_raporu_{NOW}.txt"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = payload["result"]
    parts = payload["health"]

    lines = []
    lines.append("=" * 80)
    lines.append("199 v2 PLATFORM HEALTH MANAGER")
    lines.append("=" * 80)
    lines.append(f"Tarih        : {payload['created_at']}")
    lines.append(f"Score        : {result['score']} / 100")
    lines.append(f"Decision     : {result['decision']}")
    lines.append("")
    for key, item in parts.items():
        lines.append(f"{key.upper():<15}: {item.get('status'):<8} | {item.get('message')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DETAILS")
    lines.append("-" * 80)
    lines.append(f"DB Count      : {parts['db'].get('count')}")
    lines.append(f"DB Path       : {parts['db'].get('path')}")
    lines.append(f"Disk Free     : {parts['disk'].get('free_gb')} GB")
    lines.append(f"Registry      : {parts['registry'].get('found')} / {parts['registry'].get('total')}")
    lines.append(f"Queue         : waiting={parts['queue'].get('waiting')} running={parts['queue'].get('running')} finished={parts['queue'].get('finished')} failed={parts['queue'].get('failed')}")
    lines.append(f"Workers       : idle={parts['worker'].get('idle')} running={parts['worker'].get('running')} total={parts['worker'].get('total')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")
    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")
    lines.append("")
    lines.append("NOT:")
    lines.append("199 v2 production çalıştırmaz. Platform health raporu üretir.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def main():
    ensure_dirs()
    disk = {"status": "PASS" if disk_free_gb() >= 50 else "FAIL", "free_gb": disk_free_gb(), "message": f"Disk free {disk_free_gb()} GB"}
    parts = {
        "registry": registry_health(),
        "db": discover_db(),
        "disk": disk,
        "queue": queue_health(),
        "worker": worker_health(),
        "recovery": latest_result_health("197_v4_recovery_manager_state_*.json", ["recovery clean", '"score": 100'], "Recovery"),
        "certification": latest_result_health("196_v3_certification_hardening_state_*.json", ["certified", "conditional", "not certified"], "Certification"),
        "dynamic": latest_result_health("196B_v2_controlled_dynamic_state_*.json", ["dynamic certified"], "Dynamic Certification"),
    }
    result = evaluate(parts)
    payload = {
        "module": "199 v2 Platform Health Manager",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "health": parts,
        "result": result,
    }
    json_path, txt_path = write_outputs(payload)

    print("=" * 80)
    print("199 v2 PLATFORM HEALTH MANAGER TAMAMLANDI")
    print("=" * 80)
    print(f"Score       : {result['score']} / 100")
    print(f"Decision    : {result['decision']}")
    print(f"Errors      : {len(result['errors'])}")
    print(f"Warnings    : {len(result['warnings'])}")
    print(f"DB Count    : {parts['db'].get('count')}")
    print(f"Queue       : W={parts['queue'].get('waiting')} R={parts['queue'].get('running')} F={parts['queue'].get('finished')} Fail={parts['queue'].get('failed')}")
    print(f"Workers     : idle={parts['worker'].get('idle')} running={parts['worker'].get('running')} total={parts['worker'].get('total')}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
