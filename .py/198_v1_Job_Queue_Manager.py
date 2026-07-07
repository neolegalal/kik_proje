# -*- coding: utf-8 -*-
r"""
198 v1 - Job Queue Manager
NeoLegal Production Platform v2.0

Amaç:
- 100.000+ karar üretimi için iş kuyruğu altyapısını başlatmak.
- Job ID, durum, batch büyüklüğü, worker, tarih ve retry bilgisini takip etmek.
- Bu v1 sürümü read/write olarak yalnızca queue state dosyası üretir; production çalıştırmaz.
- Paralel üretim yapmaz. Güvenli ölçekleme altyapısının ilk adımıdır.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Örnek 20 job oluşturma:
python ".py\198_v1_Job_Queue_Manager.py" --create --jobs=20 --batch=10

Kuyruk durumunu gösterme:
python ".py\198_v1_Job_Queue_Manager.py" --status

Sıradaki işi seçme:
python ".py\198_v1_Job_Queue_Manager.py" --next

Kuyruğu doğrulama:
python ".py\198_v1_Job_Queue_Manager.py" --validate
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
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

DEFAULT_JOBS = 10
DEFAULT_BATCH = 10


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_queue():
    if not QUEUE_FILE.exists():
        return {
            "module": "198 v1 Job Queue Manager",
            "created_at": now_text(),
            "updated_at": now_text(),
            "version": "v1",
            "jobs": []
        }

    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except Exception:
        backup = QUEUE_DIR / f"198_job_queue_state_corrupt_backup_{NOW}.json"
        try:
            backup.write_text(QUEUE_FILE.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        except Exception:
            pass
        return {
            "module": "198 v1 Job Queue Manager",
            "created_at": now_text(),
            "updated_at": now_text(),
            "version": "v1",
            "jobs": [],
            "warning": f"Eski queue okunamadı, backup alındı: {backup}"
        }


def save_queue(queue):
    queue["updated_at"] = now_text()
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def next_job_number(queue):
    max_no = 0
    for job in queue.get("jobs", []):
        jid = str(job.get("job_id", "JOB-000000"))
        try:
            no = int(jid.split("-")[-1])
            max_no = max(max_no, no)
        except Exception:
            pass
    return max_no + 1


def create_jobs(job_count, batch_size, label):
    queue = load_queue()
    start_no = next_job_number(queue)
    created = []

    for i in range(job_count):
        no = start_no + i
        job = {
            "job_id": f"JOB-{no:06d}",
            "status": "WAITING",
            "batch_size": batch_size,
            "label": label or f"batch_{batch_size}",
            "worker_id": None,
            "run_id": None,
            "created_at": now_text(),
            "started_at": None,
            "finished_at": None,
            "attempts": 0,
            "max_attempts": 3,
            "last_error": None,
            "notes": []
        }
        queue["jobs"].append(job)
        created.append(job)

    save_queue(queue)
    return queue, created


def summarize(queue):
    jobs = queue.get("jobs", [])
    counts = {}
    for job in jobs:
        status = job.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1

    return {
        "total": len(jobs),
        "counts": counts,
        "waiting": counts.get("WAITING", 0),
        "running": counts.get("RUNNING", 0),
        "finished": counts.get("FINISHED", 0),
        "failed": counts.get("FAILED", 0),
        "retry": counts.get("RETRY", 0),
        "cancelled": counts.get("CANCELLED", 0),
    }


def get_next_job():
    queue = load_queue()
    jobs = queue.get("jobs", [])

    for job in jobs:
        if job.get("status") in ("WAITING", "RETRY"):
            return queue, job

    return queue, None


def validate_queue(queue):
    errors = []
    warnings = []
    seen = set()

    for idx, job in enumerate(queue.get("jobs", [])):
        jid = job.get("job_id")

        if not jid:
            errors.append(f"Index {idx}: job_id yok.")
            continue

        if jid in seen:
            errors.append(f"Duplicate job_id: {jid}")
        seen.add(jid)

        status = job.get("status")
        if status not in ("WAITING", "RUNNING", "FINISHED", "FAILED", "RETRY", "CANCELLED"):
            errors.append(f"{jid}: geçersiz status: {status}")

        if job.get("status") == "RUNNING" and not job.get("started_at"):
            warnings.append(f"{jid}: RUNNING ama started_at yok.")

        if job.get("attempts", 0) > job.get("max_attempts", 3):
            warnings.append(f"{jid}: attempts max_attempts üstünde.")

        if not isinstance(job.get("batch_size"), int) or job.get("batch_size") <= 0:
            errors.append(f"{jid}: batch_size geçersiz.")

    score = 100
    score -= min(50, len(errors) * 10)
    score -= min(30, len(warnings) * 3)
    score = max(0, score)

    if errors:
        decision = "QUEUE INVALID"
    elif warnings:
        decision = "QUEUE REVIEW"
    else:
        decision = "QUEUE VALID"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_report(action, queue, extra=None):
    summary = summarize(queue)
    validation = validate_queue(queue)

    payload = {
        "module": "198 v1 Job Queue Manager",
        "created_at": now_text(),
        "action": action,
        "base_dir": str(BASE_DIR),
        "queue_file": str(QUEUE_FILE),
        "disk_free_gb": disk_free_gb(),
        "summary": summary,
        "validation": validation,
        "extra": extra or {}
    }

    json_path = STATE_DIR / f"198_v1_job_queue_manager_state_{NOW}.json"
    txt_path = REPORT_DIR / f"198_v1_job_queue_manager_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("198 v1 JOB QUEUE MANAGER")
    lines.append("=" * 80)
    lines.append(f"Tarih              : {payload['created_at']}")
    lines.append(f"Action             : {action}")
    lines.append(f"Queue File         : {QUEUE_FILE}")
    lines.append(f"Disk Free          : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("QUEUE SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Jobs         : {summary['total']}")
    lines.append(f"WAITING            : {summary['waiting']}")
    lines.append(f"RUNNING            : {summary['running']}")
    lines.append(f"FINISHED           : {summary['finished']}")
    lines.append(f"FAILED             : {summary['failed']}")
    lines.append(f"RETRY              : {summary['retry']}")
    lines.append(f"CANCELLED          : {summary['cancelled']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("VALIDATION")
    lines.append("-" * 80)
    lines.append(f"Score              : {validation['score']} / 100")
    lines.append(f"Decision           : {validation['decision']}")
    lines.append(f"Errors             : {len(validation['errors'])}")
    lines.append(f"Warnings           : {len(validation['warnings'])}")
    lines.append("")
    if validation["errors"]:
        lines.append("ERROR DETAILS")
        for e in validation["errors"]:
            lines.append(f"- {e}")
        lines.append("")
    if validation["warnings"]:
        lines.append("WARNING DETAILS")
        for w in validation["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    if extra:
        lines.append("-" * 80)
        lines.append("ACTION DETAILS")
        lines.append("-" * 80)
        for k, v in extra.items():
            lines.append(f"{k}: {v}")
        lines.append("")

    lines.append("NOT:")
    lines.append("198 v1 production çalıştırmaz ve paralel işlem yapmaz.")
    lines.append("Bu modül yalnızca güvenli iş kuyruğu altyapısını oluşturur.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true", help="Yeni job oluşturur.")
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOBS, help="Oluşturulacak job sayısı.")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="Her job için batch büyüklüğü.")
    parser.add_argument("--label", type=str, default="", help="Job etiketi.")
    parser.add_argument("--status", action="store_true", help="Kuyruk özetini gösterir.")
    parser.add_argument("--next", action="store_true", help="Sıradaki işi gösterir.")
    parser.add_argument("--validate", action="store_true", help="Kuyruğu doğrular.")
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    action = "status"
    extra = {}

    if args.create:
        if args.jobs <= 0:
            raise SystemExit("--jobs pozitif olmalı.")
        if args.batch <= 0:
            raise SystemExit("--batch pozitif olmalı.")

        queue, created = create_jobs(args.jobs, args.batch, args.label)
        action = "create"
        extra = {
            "created_jobs": len(created),
            "first_job": created[0]["job_id"] if created else None,
            "last_job": created[-1]["job_id"] if created else None,
            "batch_size": args.batch,
            "label": args.label or f"batch_{args.batch}",
        }

    else:
        queue = load_queue()

        if args.next:
            action = "next"
            _, job = get_next_job()
            if job:
                extra = {
                    "next_job_id": job.get("job_id"),
                    "next_job_status": job.get("status"),
                    "next_job_batch_size": job.get("batch_size"),
                    "next_job_attempts": job.get("attempts"),
                }
            else:
                extra = {"next_job_id": None, "message": "WAITING/RETRY job bulunamadı."}

        elif args.validate:
            action = "validate"

        elif args.status:
            action = "status"

    payload, json_path, txt_path = write_report(action, queue, extra)
    summary = payload["summary"]
    validation = payload["validation"]

    print("=" * 80)
    print("198 v1 JOB QUEUE MANAGER TAMAMLANDI")
    print("=" * 80)
    print(f"Action       : {action}")
    print(f"Total Jobs   : {summary['total']}")
    print(f"WAITING      : {summary['waiting']}")
    print(f"RUNNING      : {summary['running']}")
    print(f"FINISHED     : {summary['finished']}")
    print(f"FAILED       : {summary['failed']}")
    print(f"RETRY        : {summary['retry']}")
    print(f"Score        : {validation['score']} / 100")
    print(f"Decision     : {validation['decision']}")
    if extra:
        for k, v in extra.items():
            print(f"{k:<12}: {v}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)
    print(QUEUE_FILE)


if __name__ == "__main__":
    main()
