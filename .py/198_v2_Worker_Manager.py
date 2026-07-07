# -*- coding: utf-8 -*-
r"""
198 v2 - Worker Manager
NeoLegal Production Platform v2.0

Amaç:
- 198 v1 Job Queue Manager tarafından oluşturulan kuyruğu okumak.
- Sıradaki WAITING/RETRY işi bir worker'a atamak.
- Job status değerlerini güvenli şekilde güncellemek.
- v2 varsayılan olarak production çalıştırmaz; yalnızca worker/job state yönetir.
- 198 v3'te controlled execution entegrasyonu yapılacaktır.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Worker durumunu göster:
python ".py\198_v2_Worker_Manager.py" --status

Sıradaki işi worker-1'e ata:
python ".py\198_v2_Worker_Manager.py" --assign --worker=worker-1

Atanmış işi başarılı bitir:
python ".py\198_v2_Worker_Manager.py" --finish --worker=worker-1

Atanmış işi failed yap:
python ".py\198_v2_Worker_Manager.py" --fail --worker=worker-1 --error="test hata"

Kuyruğu ve workerları doğrula:
python ".py\198_v2_Worker_Manager.py" --validate
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
QUEUE_DIR = STATE_DIR / "job_queue"
QUEUE_FILE = QUEUE_DIR / "198_job_queue_state.json"
WORKER_FILE = QUEUE_DIR / "198_worker_state.json"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

DEFAULT_WORKERS = ["worker-1", "worker-2", "worker-3"]


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def load_json(path, default):
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


def save_json(path, data):
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
        "workers": [
            {
                "worker_id": wid,
                "status": "IDLE",
                "current_job_id": None,
                "started_at": None,
                "finished_at": None,
                "jobs_completed": 0,
                "jobs_failed": 0,
                "last_error": None,
                "notes": []
            }
            for wid in DEFAULT_WORKERS
        ]
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
    new_worker = {
        "worker_id": worker_id,
        "status": "IDLE",
        "current_job_id": None,
        "started_at": None,
        "finished_at": None,
        "jobs_completed": 0,
        "jobs_failed": 0,
        "last_error": None,
        "notes": ["Auto-created by 198 v2"]
    }
    workers.setdefault("workers", []).append(new_worker)
    return new_worker


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


def assign_job(worker_id):
    queue = load_queue()
    workers = load_workers()
    worker = get_worker(workers, worker_id)

    if worker.get("status") == "RUNNING" and worker.get("current_job_id"):
        return queue, workers, {
            "ok": False,
            "message": f"{worker_id} zaten job çalıştırıyor: {worker.get('current_job_id')}"
        }

    job = next_waiting_job(queue)
    if not job:
        return queue, workers, {
            "ok": False,
            "message": "WAITING/RETRY job bulunamadı."
        }

    job["status"] = "RUNNING"
    job["worker_id"] = worker_id
    job["started_at"] = now_text()
    job["attempts"] = int(job.get("attempts", 0)) + 1
    job.setdefault("notes", []).append(f"{now_text()} assigned to {worker_id}")

    worker["status"] = "RUNNING"
    worker["current_job_id"] = job["job_id"]
    worker["started_at"] = now_text()
    worker["finished_at"] = None
    worker["last_error"] = None

    save_queue(queue)
    save_workers(workers)

    return queue, workers, {
        "ok": True,
        "message": "Job atandı.",
        "job_id": job["job_id"],
        "worker_id": worker_id,
        "batch_size": job.get("batch_size"),
    }


def finish_job(worker_id):
    queue = load_queue()
    workers = load_workers()
    worker = get_worker(workers, worker_id)

    job_id = worker.get("current_job_id")
    if not job_id:
        return queue, workers, {
            "ok": False,
            "message": f"{worker_id} üzerinde aktif job yok."
        }

    job = find_job(queue, job_id)
    if not job:
        return queue, workers, {
            "ok": False,
            "message": f"Worker current_job_id queue içinde bulunamadı: {job_id}"
        }

    job["status"] = "FINISHED"
    job["finished_at"] = now_text()
    job.setdefault("notes", []).append(f"{now_text()} finished by {worker_id}")

    worker["status"] = "IDLE"
    worker["current_job_id"] = None
    worker["finished_at"] = now_text()
    worker["jobs_completed"] = int(worker.get("jobs_completed", 0)) + 1

    save_queue(queue)
    save_workers(workers)

    return queue, workers, {
        "ok": True,
        "message": "Job FINISHED yapıldı.",
        "job_id": job_id,
        "worker_id": worker_id,
    }


def fail_job(worker_id, error_message):
    queue = load_queue()
    workers = load_workers()
    worker = get_worker(workers, worker_id)

    job_id = worker.get("current_job_id")
    if not job_id:
        return queue, workers, {
            "ok": False,
            "message": f"{worker_id} üzerinde aktif job yok."
        }

    job = find_job(queue, job_id)
    if not job:
        return queue, workers, {
            "ok": False,
            "message": f"Worker current_job_id queue içinde bulunamadı: {job_id}"
        }

    attempts = int(job.get("attempts", 0))
    max_attempts = int(job.get("max_attempts", 3))

    if attempts < max_attempts:
        job["status"] = "RETRY"
    else:
        job["status"] = "FAILED"

    job["last_error"] = error_message
    job["finished_at"] = now_text()
    job.setdefault("notes", []).append(f"{now_text()} failed by {worker_id}: {error_message}")

    worker["status"] = "IDLE"
    worker["current_job_id"] = None
    worker["finished_at"] = now_text()
    worker["jobs_failed"] = int(worker.get("jobs_failed", 0)) + 1
    worker["last_error"] = error_message

    save_queue(queue)
    save_workers(workers)

    return queue, workers, {
        "ok": True,
        "message": f"Job {job['status']} yapıldı.",
        "job_id": job_id,
        "worker_id": worker_id,
        "job_status": job["status"],
        "attempts": attempts,
        "max_attempts": max_attempts,
    }


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
        "cancelled": counts.get("CANCELLED", 0),
        "unknown": counts.get("UNKNOWN", 0),
        "counts": counts,
    }


def worker_summary(workers):
    counts = {}
    for w in workers.get("workers", []):
        status = w.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    return {
        "total": len(workers.get("workers", [])),
        "idle": counts.get("IDLE", 0),
        "running": counts.get("RUNNING", 0),
        "disabled": counts.get("DISABLED", 0),
        "unknown": counts.get("UNKNOWN", 0),
        "counts": counts,
    }


def validate(queue, workers):
    errors = []
    warnings = []

    job_ids = set()
    running_jobs = set()

    for job in queue.get("jobs", []):
        jid = job.get("job_id")
        if not jid:
            errors.append("job_id eksik job var.")
            continue

        if jid in job_ids:
            errors.append(f"Duplicate job_id: {jid}")
        job_ids.add(jid)

        status = job.get("status")
        if status not in ("WAITING", "RUNNING", "FINISHED", "FAILED", "RETRY", "CANCELLED"):
            errors.append(f"{jid}: geçersiz status: {status}")

        if status == "RUNNING":
            running_jobs.add(jid)
            if not job.get("worker_id"):
                errors.append(f"{jid}: RUNNING ama worker_id yok.")
            if not job.get("started_at"):
                warnings.append(f"{jid}: RUNNING ama started_at yok.")

    worker_running_jobs = set()

    for w in workers.get("workers", []):
        wid = w.get("worker_id")
        status = w.get("status")

        if not wid:
            errors.append("worker_id eksik worker var.")
            continue

        if status not in ("IDLE", "RUNNING", "DISABLED"):
            errors.append(f"{wid}: geçersiz worker status: {status}")

        current = w.get("current_job_id")

        if status == "RUNNING":
            if not current:
                errors.append(f"{wid}: RUNNING ama current_job_id yok.")
            else:
                worker_running_jobs.add(current)
                if current not in job_ids:
                    errors.append(f"{wid}: current_job_id queue içinde yok: {current}")

        if status == "IDLE" and current:
            warnings.append(f"{wid}: IDLE ama current_job_id dolu: {current}")

    if running_jobs != worker_running_jobs:
        warnings.append(
            f"Queue RUNNING job seti ile worker current job seti farklı. queue={sorted(running_jobs)}, workers={sorted(worker_running_jobs)}"
        )

    score = 100
    score -= min(50, len(errors) * 10)
    score -= min(30, len(warnings) * 3)
    score = max(0, score)

    if errors:
        decision = "WORKER QUEUE INVALID"
    elif warnings:
        decision = "WORKER QUEUE REVIEW"
    else:
        decision = "WORKER QUEUE VALID"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_report(action, queue, workers, operation_result=None):
    qsum = queue_summary(queue)
    wsum = worker_summary(workers)
    val = validate(queue, workers)

    payload = {
        "module": "198 v2 Worker Manager",
        "created_at": now_text(),
        "action": action,
        "base_dir": str(BASE_DIR),
        "queue_file": str(QUEUE_FILE),
        "worker_file": str(WORKER_FILE),
        "disk_free_gb": disk_free_gb(),
        "queue_summary": qsum,
        "worker_summary": wsum,
        "validation": val,
        "operation_result": operation_result or {},
    }

    json_path = STATE_DIR / f"198_v2_worker_manager_state_{NOW}.json"
    txt_path = REPORT_DIR / f"198_v2_worker_manager_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("198 v2 WORKER MANAGER")
    lines.append("=" * 80)
    lines.append(f"Tarih              : {payload['created_at']}")
    lines.append(f"Action             : {action}")
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
    lines.append("WORKER SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Workers      : {wsum['total']}")
    lines.append(f"IDLE               : {wsum['idle']}")
    lines.append(f"RUNNING            : {wsum['running']}")
    lines.append(f"DISABLED           : {wsum['disabled']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("VALIDATION")
    lines.append("-" * 80)
    lines.append(f"Score              : {val['score']} / 100")
    lines.append(f"Decision           : {val['decision']}")
    lines.append(f"Errors             : {len(val['errors'])}")
    lines.append(f"Warnings           : {len(val['warnings'])}")
    if val["errors"]:
        lines.append("")
        lines.append("ERROR DETAILS")
        for e in val["errors"]:
            lines.append(f"- {e}")
    if val["warnings"]:
        lines.append("")
        lines.append("WARNING DETAILS")
        for w in val["warnings"]:
            lines.append(f"- {w}")

    if operation_result:
        lines.append("")
        lines.append("-" * 80)
        lines.append("OPERATION RESULT")
        lines.append("-" * 80)
        for k, v in operation_result.items():
            lines.append(f"{k}: {v}")

    lines.append("")
    lines.append("NOT:")
    lines.append("198 v2 production çalıştırmaz. Worker/job state yönetimini test eder.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))
    lines.append(str(QUEUE_FILE))
    lines.append(str(WORKER_FILE))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true", help="Kuyruk ve worker durumunu gösterir.")
    parser.add_argument("--assign", action="store_true", help="Sıradaki job'u worker'a atar.")
    parser.add_argument("--finish", action="store_true", help="Worker üzerindeki aktif job'u FINISHED yapar.")
    parser.add_argument("--fail", action="store_true", help="Worker üzerindeki aktif job'u RETRY/FAILED yapar.")
    parser.add_argument("--validate", action="store_true", help="Kuyruk-worker tutarlılığını doğrular.")
    parser.add_argument("--worker", type=str, default="worker-1", help="Worker ID")
    parser.add_argument("--error", type=str, default="manual failure", help="Fail mesajı")
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    action = "status"
    operation = {}

    if args.assign:
        action = "assign"
        queue, workers, operation = assign_job(args.worker)
    elif args.finish:
        action = "finish"
        queue, workers, operation = finish_job(args.worker)
    elif args.fail:
        action = "fail"
        queue, workers, operation = fail_job(args.worker, args.error)
    else:
        queue = load_queue()
        workers = load_workers()
        save_workers(workers)  # worker state ilk kez yoksa oluşturur
        if args.validate:
            action = "validate"
        else:
            action = "status"

    payload, json_path, txt_path = write_report(action, queue, workers, operation)
    qsum = payload["queue_summary"]
    wsum = payload["worker_summary"]
    val = payload["validation"]

    print("=" * 80)
    print("198 v2 WORKER MANAGER TAMAMLANDI")
    print("=" * 80)
    print(f"Action       : {action}")
    print(f"Queue Jobs   : {qsum['total']}")
    print(f"WAITING      : {qsum['waiting']}")
    print(f"RUNNING      : {qsum['running']}")
    print(f"FINISHED     : {qsum['finished']}")
    print(f"FAILED       : {qsum['failed']}")
    print(f"RETRY        : {qsum['retry']}")
    print(f"Workers      : {wsum['total']}")
    print(f"IDLE         : {wsum['idle']}")
    print(f"W-RUNNING    : {wsum['running']}")
    print(f"Score        : {val['score']} / 100")
    print(f"Decision     : {val['decision']}")
    if operation:
        for k, v in operation.items():
            print(f"{k:<12}: {v}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)
    print(QUEUE_FILE)
    print(WORKER_FILE)


if __name__ == "__main__":
    main()
