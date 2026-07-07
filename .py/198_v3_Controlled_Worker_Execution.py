# -*- coding: utf-8 -*-
r"""
198 v3 - Controlled Worker Execution
NeoLegal Production Platform v2.0

Amaç:
- 198 v1 job queue ve 198 v2 worker state yapısını kullanmak.
- Sıradaki WAITING/RETRY job'u worker'a atamak.
- Job'un batch_size değerine göre 181 Production Controller'ı kontrollü çalıştırmak.
- DB before/after farkını ölçmek.
- Job'u FINISHED / RETRY / FAILED durumuna almak.
- Bu sürüm tek worker kontrollü execution içindir; gerçek paralellik yapmaz.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Dry-run:
python ".py\198_v3_Controlled_Worker_Execution.py" --worker=worker-1

Gerçek kontrollü execution:
python ".py\198_v3_Controlled_Worker_Execution.py" --worker=worker-1 --execute --timeout=3600

Sadece 1 job çalıştırır.
"""

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
QUEUE_DIR = STATE_DIR / "job_queue"

QUEUE_FILE = QUEUE_DIR / "198_job_queue_state.json"
WORKER_FILE = QUEUE_DIR / "198_worker_state.json"

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")
DEFAULT_TIMEOUT_SECONDS = 60 * 60


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        backup = path.with_name(path.stem + f"_corrupt_backup_{NOW}" + path.suffix)
        try:
            backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        except Exception:
            pass
        default["warning"] = f"Dosya okunamadı; backup alındı: {backup}"
        return default


def save_json(path: Path, data):
    data["updated_at"] = now_text()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def default_queue():
    return {
        "module": "198 v1 Job Queue Manager",
        "created_at": now_text(),
        "updated_at": now_text(),
        "version": "v1",
        "jobs": []
    }


def default_workers():
    return {
        "module": "198 v2 Worker Manager",
        "created_at": now_text(),
        "updated_at": now_text(),
        "version": "v2",
        "workers": []
    }


def load_queue():
    return load_json(QUEUE_FILE, default_queue())


def save_queue(queue):
    save_json(QUEUE_FILE, queue)


def load_workers():
    return load_json(WORKER_FILE, default_workers())


def save_workers(workers):
    save_json(WORKER_FILE, workers)


def get_worker(workers, worker_id):
    for w in workers.get("workers", []):
        if w.get("worker_id") == worker_id:
            return w

    worker = {
        "worker_id": worker_id,
        "status": "IDLE",
        "current_job_id": None,
        "started_at": None,
        "finished_at": None,
        "jobs_completed": 0,
        "jobs_failed": 0,
        "last_error": None,
        "notes": ["Auto-created by 198 v3"]
    }
    workers.setdefault("workers", []).append(worker)
    return worker


def find_job(queue, job_id):
    for job in queue.get("jobs", []):
        if job.get("job_id") == job_id:
            return job
    return None


def next_waiting_job(queue):
    for job in queue.get("jobs", []):
        if job.get("status") in ("WAITING", "RETRY"):
            return job
    return None


def queue_summary(queue):
    counts = {}
    for job in queue.get("jobs", []):
        status = job.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    return {
        "total": len(queue.get("jobs", [])),
        "waiting": counts.get("WAITING", 0),
        "running": counts.get("RUNNING", 0),
        "finished": counts.get("FINISHED", 0),
        "failed": counts.get("FAILED", 0),
        "retry": counts.get("RETRY", 0),
        "counts": counts,
    }


def discover_db():
    candidates = []
    for p in BASE_DIR.rglob("*.db"):
        if "kik" in p.name.lower():
            candidates.append(p)
    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not candidates:
        return {"status": "FAIL", "path": None, "table": None, "count": None, "message": "KİK DB bulunamadı."}

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
            return {"status": "FAIL", "path": str(db_path), "table": None, "count": None, "message": "DB var ancak tablo yok."}

        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()

        return {"status": "PASS", "path": str(db_path), "table": table, "count": count, "message": f"DB bulundu. Tablo={table}, kayıt={count}"}

    except Exception as e:
        return {"status": "FAIL", "path": str(db_path), "table": None, "count": None, "message": f"DB okunamadı: {e}"}


def db_count(db_info):
    if not db_info.get("path") or not db_info.get("table"):
        return None
    try:
        conn = sqlite3.connect(db_info["path"])
        cur = conn.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM {db_info['table']}").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return None


def find_production_controller():
    candidates = []
    if PY_DIR.exists():
        candidates.extend(PY_DIR.glob("181*.py"))
        candidates.extend(PY_DIR.glob("*181*.py"))
    candidates = list(set(candidates))
    candidates = [p for p in candidates if "198" not in p.name]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def build_command(script_path: str, batch_size: int):
    return [sys.executable, script_path, f"--batch={batch_size}"]


def run_command(command, timeout_seconds):
    started = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout_seconds
        )
        elapsed = round(time.time() - started, 2)
        return {
            "executed": True,
            "timeout": False,
            "returncode": proc.returncode,
            "elapsed_seconds": elapsed,
            "stdout_tail": proc.stdout[-12000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-12000:] if proc.stderr else "",
            "status": "PASS" if proc.returncode == 0 else "FAIL"
        }
    except subprocess.TimeoutExpired as e:
        elapsed = round(time.time() - started, 2)
        return {
            "executed": True,
            "timeout": True,
            "returncode": None,
            "elapsed_seconds": elapsed,
            "stdout_tail": (e.stdout or "")[-12000:] if isinstance(e.stdout, str) else "",
            "stderr_tail": (e.stderr or "")[-12000:] if isinstance(e.stderr, str) else "",
            "status": "TIMEOUT"
        }
    except Exception as e:
        elapsed = round(time.time() - started, 2)
        return {
            "executed": True,
            "timeout": False,
            "returncode": None,
            "elapsed_seconds": elapsed,
            "stdout_tail": "",
            "stderr_tail": str(e),
            "status": "FAIL"
        }


def mark_running(queue, workers, job, worker, execute):
    job["status"] = "RUNNING"
    job["worker_id"] = worker["worker_id"]
    job["started_at"] = now_text()
    job["attempts"] = int(job.get("attempts", 0)) + 1
    job.setdefault("notes", []).append(f"{now_text()} assigned/executed by 198 v3 worker={worker['worker_id']} execute={execute}")

    worker["status"] = "RUNNING"
    worker["current_job_id"] = job["job_id"]
    worker["started_at"] = now_text()
    worker["finished_at"] = None
    worker["last_error"] = None

    save_queue(queue)
    save_workers(workers)


def mark_finished(queue, workers, job, worker, run_result, db_before, db_after):
    job["status"] = "FINISHED"
    job["finished_at"] = now_text()
    job["last_error"] = None
    job["db_before"] = db_before
    job["db_after"] = db_after
    job["db_delta"] = None if db_before is None or db_after is None else db_after - db_before
    job["last_run_status"] = run_result.get("status")
    job["last_returncode"] = run_result.get("returncode")
    job.setdefault("notes", []).append(f"{now_text()} finished by 198 v3")

    worker["status"] = "IDLE"
    worker["current_job_id"] = None
    worker["finished_at"] = now_text()
    worker["jobs_completed"] = int(worker.get("jobs_completed", 0)) + 1
    worker["last_error"] = None

    save_queue(queue)
    save_workers(workers)


def mark_failed(queue, workers, job, worker, error_message, run_result=None, db_before=None, db_after=None):
    attempts = int(job.get("attempts", 0))
    max_attempts = int(job.get("max_attempts", 3))

    if attempts < max_attempts:
        job["status"] = "RETRY"
    else:
        job["status"] = "FAILED"

    job["finished_at"] = now_text()
    job["last_error"] = error_message
    job["db_before"] = db_before
    job["db_after"] = db_after
    job["db_delta"] = None if db_before is None or db_after is None else db_after - db_before

    if run_result:
        job["last_run_status"] = run_result.get("status")
        job["last_returncode"] = run_result.get("returncode")

    job.setdefault("notes", []).append(f"{now_text()} failed by 198 v3: {error_message}")

    worker["status"] = "IDLE"
    worker["current_job_id"] = None
    worker["finished_at"] = now_text()
    worker["jobs_failed"] = int(worker.get("jobs_failed", 0)) + 1
    worker["last_error"] = error_message

    save_queue(queue)
    save_workers(workers)


def validate_state(queue, workers):
    errors = []
    warnings = []
    job_ids = {j.get("job_id") for j in queue.get("jobs", []) if j.get("job_id")}
    running_jobs = {j.get("job_id") for j in queue.get("jobs", []) if j.get("status") == "RUNNING"}
    worker_jobs = set()

    for w in workers.get("workers", []):
        if w.get("status") == "RUNNING" and w.get("current_job_id"):
            worker_jobs.add(w.get("current_job_id"))
            if w.get("current_job_id") not in job_ids:
                errors.append(f"Worker job queue içinde yok: {w.get('current_job_id')}")

    if running_jobs != worker_jobs:
        warnings.append(f"RUNNING job-worker farkı: queue={sorted(running_jobs)}, workers={sorted(worker_jobs)}")

    score = 100 - min(50, len(errors) * 10) - min(30, len(warnings) * 3)
    score = max(0, score)

    return {
        "score": score,
        "decision": "VALID" if not errors and not warnings else ("INVALID" if errors else "REVIEW"),
        "errors": errors,
        "warnings": warnings
    }


def execute_one(worker_id, execute, timeout_seconds):
    queue = load_queue()
    workers = load_workers()
    worker = get_worker(workers, worker_id)

    if worker.get("status") == "RUNNING" and worker.get("current_job_id"):
        return queue, workers, {
            "ok": False,
            "stage": "precheck",
            "message": f"{worker_id} zaten RUNNING: {worker.get('current_job_id')}"
        }

    job = next_waiting_job(queue)
    if not job:
        return queue, workers, {
            "ok": False,
            "stage": "precheck",
            "message": "WAITING/RETRY job bulunamadı."
        }

    controller = find_production_controller()
    if not controller:
        return queue, workers, {
            "ok": False,
            "stage": "precheck",
            "message": "181 Production Controller bulunamadı."
        }

    batch_size = int(job.get("batch_size", 1))
    command = build_command(str(controller), batch_size)
    db_info = discover_db()
    db_before = db_info.get("count")

    operation = {
        "ok": True,
        "job_id": job.get("job_id"),
        "worker_id": worker_id,
        "batch_size": batch_size,
        "controller": str(controller),
        "command": " ".join(command),
        "execute": execute,
        "db_before": db_before,
        "db_after": None,
        "db_delta": None,
        "run_result": None,
    }

    if not execute:
        operation["stage"] = "dry_run"
        operation["message"] = "Dry-run: job atanmadı ve production çalıştırılmadı."
        return queue, workers, operation

    mark_running(queue, workers, job, worker, execute=True)

    run_result = run_command(command, timeout_seconds)
    db_after = db_count(db_info)

    operation["run_result"] = run_result
    operation["db_after"] = db_after
    operation["db_delta"] = None if db_before is None or db_after is None else db_after - db_before

    if run_result.get("status") == "PASS":
        mark_finished(queue, workers, job, worker, run_result, db_before, db_after)
        operation["stage"] = "finished"
        operation["message"] = "Job başarıyla FINISHED yapıldı."
    else:
        err = f"Production run başarısız: {run_result.get('status')}"
        mark_failed(queue, workers, job, worker, err, run_result, db_before, db_after)
        operation["ok"] = False
        operation["stage"] = "failed"
        operation["message"] = err

    queue = load_queue()
    workers = load_workers()
    return queue, workers, operation


def evaluate(queue, workers, operation):
    score = 100
    errors = []
    warnings = []

    validation = validate_state(queue, workers)
    if validation["errors"]:
        score -= 30
        errors.extend(validation["errors"])
    if validation["warnings"]:
        score -= 10
        warnings.extend(validation["warnings"])

    if not operation.get("ok"):
        score -= 20
        errors.append(operation.get("message", "Operation failed"))

    if not operation.get("execute"):
        score -= 10
        warnings.append("Dry-run: gerçek production çalıştırılmadı.")

    rr = operation.get("run_result")
    if rr:
        if rr.get("status") != "PASS":
            score -= 25
            errors.append("Production subprocess PASS dönmedi.")
        if operation.get("db_delta") == 0:
            warnings.append("DB delta 0. Üretim kontrol modunda çalışmış olabilir.")
        elif operation.get("db_delta") is not None and operation.get("db_delta") < 0:
            score -= 25
            errors.append("DB kayıt sayısı azaldı.")
        elif operation.get("db_delta") is not None and operation.get("db_delta") > 0:
            warnings.append(f"DB artışı tespit edildi: +{operation.get('db_delta')}")

    score = max(0, min(100, score))

    if errors:
        decision = "WORKER EXECUTION FAILED"
    elif operation.get("execute") and score >= 90:
        decision = "WORKER EXECUTION CERTIFIED"
    elif operation.get("execute") and score >= 75:
        decision = "WORKER EXECUTION REVIEW"
    else:
        decision = "READY FOR WORKER EXECUTION"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "state_validation": validation,
    }


def write_report(queue, workers, operation, result):
    qsum = queue_summary(queue)

    payload = {
        "module": "198 v3 Controlled Worker Execution",
        "created_at": now_text(),
        "base_dir": str(BASE_DIR),
        "queue_file": str(QUEUE_FILE),
        "worker_file": str(WORKER_FILE),
        "disk_free_gb": disk_free_gb(),
        "queue_summary": qsum,
        "operation": operation,
        "result": result,
    }

    json_path = STATE_DIR / f"198_v3_controlled_worker_execution_state_{NOW}.json"
    txt_path = REPORT_DIR / f"198_v3_controlled_worker_execution_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("198 v3 CONTROLLED WORKER EXECUTION")
    lines.append("=" * 80)
    lines.append(f"Tarih              : {payload['created_at']}")
    lines.append(f"Score              : {result['score']} / 100")
    lines.append(f"Decision           : {result['decision']}")
    lines.append(f"Disk Free          : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("QUEUE SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Jobs         : {qsum['total']}")
    lines.append(f"WAITING            : {qsum['waiting']}")
    lines.append(f"RUNNING            : {qsum['running']}")
    lines.append(f"FINISHED           : {qsum['finished']}")
    lines.append(f"FAILED             : {qsum['failed']}")
    lines.append(f"RETRY              : {qsum['retry']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("OPERATION")
    lines.append("-" * 80)
    for k, v in operation.items():
        if k == "run_result":
            continue
        lines.append(f"{k}: {v}")
    lines.append("")
    rr = operation.get("run_result")
    if rr:
        lines.append("RUN RESULT")
        lines.append(f"status: {rr.get('status')}")
        lines.append(f"returncode: {rr.get('returncode')}")
        lines.append(f"timeout: {rr.get('timeout')}")
        lines.append(f"elapsed_seconds: {rr.get('elapsed_seconds')}")
        lines.append("")
        lines.append("STDOUT TAIL")
        lines.append(rr.get("stdout_tail") or "")
        lines.append("")
        lines.append("STDERR TAIL")
        lines.append(rr.get("stderr_tail") or "")
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
    lines.append("198 v3 tek worker/tek job kontrollü execution yapar. Paralel çalıştırma yapmaz.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=str, default="worker-1", help="Worker ID")
    parser.add_argument("--execute", action="store_true", help="Gerçek production çalıştırır.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Timeout saniye.")
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    queue, workers, operation = execute_one(args.worker, args.execute, args.timeout)
    result = evaluate(queue, workers, operation)
    payload, json_path, txt_path = write_report(queue, workers, operation, result)
    qsum = payload["queue_summary"]

    print("=" * 80)
    print("198 v3 CONTROLLED WORKER EXECUTION TAMAMLANDI")
    print("=" * 80)
    print(f"Execute       : {args.execute}")
    print(f"Worker        : {args.worker}")
    print(f"Score         : {result['score']} / 100")
    print(f"Decision      : {result['decision']}")
    print(f"Errors        : {len(result['errors'])}")
    print(f"Warnings      : {len(result['warnings'])}")
    print(f"Job ID        : {operation.get('job_id')}")
    print(f"Batch Size    : {operation.get('batch_size')}")
    print(f"Stage         : {operation.get('stage')}")
    print(f"DB Before     : {operation.get('db_before')}")
    print(f"DB After      : {operation.get('db_after')}")
    print(f"DB Delta      : {operation.get('db_delta')}")
    print(f"WAITING       : {qsum['waiting']}")
    print(f"RUNNING       : {qsum['running']}")
    print(f"FINISHED      : {qsum['finished']}")
    print(f"FAILED        : {qsum['failed']}")
    print(f"RETRY         : {qsum['retry']}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
