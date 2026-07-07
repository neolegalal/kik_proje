# -*- coding: utf-8 -*-
import json
import sqlite3
from pathlib import Path
from config import BASE_DIR, STATE_DIR, QUEUE_FILE, WORKER_FILE, EVENT_LOG, PLATFORM_LOG
from utils import safe_json, safe_read, disk_free_gb, latest_file

def collect_db_metrics():
    candidates = [p for p in BASE_DIR.rglob("*.db") if "kik" in p.name.lower()]
    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return {"status": "FAIL", "count": 0, "path": None, "message": "DB bulunamadı."}
    db_path = candidates[0]
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        table = "hukuki_kartlar" if "hukuki_kartlar" in tables else (tables[0] if tables else None)
        if not table:
            conn.close()
            return {"status": "FAIL", "count": 0, "path": str(db_path), "message": "Tablo yok."}
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return {"status": "PASS", "count": count, "path": str(db_path), "table": table, "message": f"DB OK: {count}"}
    except Exception as e:
        return {"status": "FAIL", "count": 0, "path": str(db_path), "message": str(e)}

def collect_queue_metrics():
    q = safe_json(QUEUE_FILE)
    if not q:
        return {"status": "WARNING", "total": 0, "message": "Queue yok veya okunamadı."}
    jobs = q.get("jobs", [])
    counts = {}
    for j in jobs:
        st = j.get("status", "UNKNOWN")
        counts[st] = counts.get(st, 0) + 1
    total = len(jobs)
    finished = counts.get("FINISHED", 0)
    failed = counts.get("FAILED", 0)
    completion_rate = round((finished / total) * 100, 2) if total else 0
    return {
        "status": "PASS" if failed == 0 else "WARNING",
        "total": total,
        "waiting": counts.get("WAITING", 0),
        "running": counts.get("RUNNING", 0),
        "finished": finished,
        "failed": failed,
        "retry": counts.get("RETRY", 0),
        "completion_rate": completion_rate,
        "message": f"Queue total={total}, finished={finished}, failed={failed}"
    }

def collect_worker_metrics():
    w = safe_json(WORKER_FILE)
    if not w:
        return {"status": "WARNING", "total": 0, "message": "Worker state yok veya okunamadı."}
    workers = w.get("workers", [])
    counts = {}
    completed = 0
    failed = 0
    for worker in workers:
        st = worker.get("status", "UNKNOWN")
        counts[st] = counts.get(st, 0) + 1
        completed += int(worker.get("jobs_completed", 0) or 0)
        failed += int(worker.get("jobs_failed", 0) or 0)
    return {
        "status": "PASS",
        "total": len(workers),
        "idle": counts.get("IDLE", 0),
        "running": counts.get("RUNNING", 0),
        "disabled": counts.get("DISABLED", 0),
        "jobs_completed": completed,
        "jobs_failed": failed,
        "message": f"Workers total={len(workers)}, idle={counts.get('IDLE', 0)}"
    }

def collect_jsonl_metrics(path, type_field, severity_field=None):
    path = Path(path)
    if not path.exists():
        return {"status": "WARNING", "total": 0, "invalid": 0, "by_type": {}, "by_severity": {}, "message": f"{path.name} yok."}
    total = 0
    invalid = 0
    by_type = {}
    by_severity = {}
    for line in safe_read(path).splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            total += 1
            typ = obj.get(type_field, "UNKNOWN")
            by_type[typ] = by_type.get(typ, 0) + 1
            if severity_field:
                sev = obj.get(severity_field, "UNKNOWN")
                by_severity[sev] = by_severity.get(sev, 0) + 1
        except Exception:
            invalid += 1
    status = "PASS" if invalid == 0 else "WARNING"
    return {"status": status, "total": total, "invalid": invalid, "by_type": by_type, "by_severity": by_severity, "message": f"{path.name} total={total}, invalid={invalid}"}

def collect_latest_run_metrics():
    patterns = {
        "platform_core": "200_pkg_core_state_*.json",
        "event_audit": "201_v3_event_bus_auditor_state_*.json",
        "scheduler_engine": "202_v2_scheduler_engine_state_*.json",
        "logger_audit": "203_logger_audit_state_*.json",
        "docs_manager": "206*",
    }
    latest = {}
    for key, pattern in patterns.items():
        f = latest_file(STATE_DIR, pattern)
        latest[key] = str(f) if f else None
    return latest

def collect_all():
    return {
        "disk": {"free_gb": disk_free_gb(BASE_DIR), "status": "PASS" if disk_free_gb(BASE_DIR) >= 50 else "FAIL"},
        "db": collect_db_metrics(),
        "queue": collect_queue_metrics(),
        "workers": collect_worker_metrics(),
        "events": collect_jsonl_metrics(EVENT_LOG, "event_type", "severity"),
        "logs": collect_jsonl_metrics(PLATFORM_LOG, "source", "level"),
        "latest_runs": collect_latest_run_metrics(),
    }
