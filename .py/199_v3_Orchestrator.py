# -*- coding: utf-8 -*-
r"""
199 v3 - Orchestrator
NeoLegal Production Platform v2.0

Amaç:
- 199 v2 Platform Health Manager ile sağlık kontrolü yapmak.
- Platform READY ise 198 v3 Controlled Worker Execution komutunu kurmak.
- Varsayılan olarak DRY RUN çalışır.
- --execute verilirse 198 v3 üzerinden tek job / tek worker gerçek production execution yapar.
- 199 artık üst yönetici katman olarak çalışmaya başlar.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Dry-run:
python ".py\199_v3_Orchestrator.py" --worker=worker-1

Gerçek execution:
python ".py\199_v3_Orchestrator.py" --worker=worker-1 --execute --timeout=3600
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

DEFAULT_TIMEOUT = 3600


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


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


def safe_read(path: Path, limit_chars=300000):
    if not path:
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")[:limit_chars]
        except Exception:
            pass
    return ""


def safe_json(path: Path):
    if not path or not path.exists():
        return None
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None


def find_script(prefix: str, must_contain=None):
    must_contain = must_contain or []
    if not PY_DIR.exists():
        return None

    candidates = []
    candidates.extend(PY_DIR.glob(f"{prefix}*.py"))
    candidates.extend(PY_DIR.glob(f"*{prefix}*.py"))
    candidates = list(set(candidates))

    if must_contain:
        filtered = []
        for p in candidates:
            name = p.name.lower()
            if all(tok.lower() in name for tok in must_contain):
                filtered.append(p)
        candidates = filtered

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def run_command(command, timeout):
    started = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout
        )
        return {
            "executed": True,
            "timeout": False,
            "returncode": proc.returncode,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": proc.stdout[-12000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-12000:] if proc.stderr else "",
            "status": "PASS" if proc.returncode == 0 else "FAIL"
        }
    except subprocess.TimeoutExpired as e:
        return {
            "executed": True,
            "timeout": True,
            "returncode": None,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": (e.stdout or "")[-12000:] if isinstance(e.stdout, str) else "",
            "stderr_tail": (e.stderr or "")[-12000:] if isinstance(e.stderr, str) else "",
            "status": "TIMEOUT"
        }
    except Exception as e:
        return {
            "executed": True,
            "timeout": False,
            "returncode": None,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": "",
            "stderr_tail": str(e),
            "status": "FAIL"
        }


def run_health_check(timeout=600):
    script = find_script("199", ["v2", "platform", "health"])
    if not script:
        return {
            "script": None,
            "command": None,
            "run_result": None,
            "latest_state": None,
            "decision": "HEALTH SCRIPT MISSING",
            "score": 0,
            "status": "FAIL"
        }

    command = [sys.executable, str(script)]
    rr = run_command(command, timeout)
    latest = latest_file(STATE_DIR, "199_v2_platform_health_state_*.json")
    data = safe_json(latest)
    result = (data or {}).get("result", {})
    decision = result.get("decision", "UNKNOWN")
    score = result.get("score", 0)

    status = "PASS" if rr.get("status") == "PASS" and decision == "PLATFORM READY" else "WARNING"
    if rr.get("status") != "PASS":
        status = "FAIL"

    return {
        "script": str(script),
        "command": " ".join(command),
        "run_result": rr,
        "latest_state": str(latest) if latest else None,
        "decision": decision,
        "score": score,
        "status": status
    }


def build_worker_command(worker, execute, timeout):
    script = find_script("198", ["v3", "controlled", "worker"])
    if not script:
        return None, None

    command = [sys.executable, str(script), f"--worker={worker}", f"--timeout={timeout}"]
    if execute:
        command.append("--execute")
    return script, command


def evaluate(payload):
    score = 100
    errors = []
    warnings = []

    health = payload["health_check"]
    if health["status"] == "FAIL":
        score -= 40
        errors.append("Health check çalışmadı veya başarısız.")
    elif health["decision"] != "PLATFORM READY":
        score -= 25
        errors.append(f"Platform READY değil: {health['decision']}")

    if not payload.get("worker_script"):
        score -= 30
        errors.append("198 v3 Controlled Worker Execution script bulunamadı.")

    if not payload["execute"]:
        score -= 10
        warnings.append("Dry-run: 198 v3 gerçek execution çalıştırılmadı.")

    wr = payload.get("worker_run_result")
    if payload["execute"]:
        if not wr:
            score -= 30
            errors.append("Execute istendi ancak worker_run_result yok.")
        elif wr.get("status") != "PASS":
            score -= 30
            errors.append(f"Worker execution subprocess başarısız: {wr.get('status')}")

        latest = payload.get("latest_worker_state_data") or {}
        decision = (latest.get("result") or {}).get("decision")
        if decision != "WORKER EXECUTION CERTIFIED":
            score -= 15
            warnings.append(f"Worker execution decision beklenen değil: {decision}")

    score = max(0, min(100, score))

    if errors:
        decision = "ORCHESTRATOR BLOCKED"
    elif payload["execute"] and score >= 90:
        decision = "ORCHESTRATOR CERTIFIED"
    elif payload["execute"] and score >= 75:
        decision = "ORCHESTRATOR REVIEW"
    else:
        decision = "READY FOR ORCHESTRATION EXECUTE"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_outputs(payload):
    json_path = STATE_DIR / f"199_v3_orchestrator_state_{NOW}.json"
    txt_path = REPORT_DIR / f"199_v3_orchestrator_raporu_{NOW}.txt"

    payload["result"] = evaluate(payload)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = payload["result"]

    lines = []
    lines.append("=" * 80)
    lines.append("199 v3 ORCHESTRATOR")
    lines.append("=" * 80)
    lines.append(f"Tarih             : {payload['created_at']}")
    lines.append(f"Execute           : {payload['execute']}")
    lines.append(f"Worker            : {payload['worker']}")
    lines.append(f"Score             : {result['score']} / 100")
    lines.append(f"Decision          : {result['decision']}")
    lines.append(f"Disk Free         : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("HEALTH CHECK")
    lines.append("-" * 80)
    h = payload["health_check"]
    lines.append(f"Status            : {h.get('status')}")
    lines.append(f"Decision          : {h.get('decision')}")
    lines.append(f"Score             : {h.get('score')}")
    lines.append(f"Script            : {h.get('script')}")
    lines.append(f"State             : {h.get('latest_state')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("WORKER EXECUTION")
    lines.append("-" * 80)
    lines.append(f"Worker Script     : {payload.get('worker_script')}")
    lines.append(f"Worker Command    : {payload.get('worker_command')}")
    wr = payload.get("worker_run_result")
    if wr:
        lines.append(f"Run Status        : {wr.get('status')}")
        lines.append(f"Return Code       : {wr.get('returncode')}")
        lines.append(f"Elapsed Seconds   : {wr.get('elapsed_seconds')}")
        lines.append("")
        lines.append("STDOUT TAIL")
        lines.append(wr.get("stdout_tail") or "")
        lines.append("")
        lines.append("STDERR TAIL")
        lines.append(wr.get("stderr_tail") or "")
    else:
        lines.append("Worker execution çalıştırılmadı.")
    lines.append("")
    latest_worker = payload.get("latest_worker_state_data") or {}
    if latest_worker:
        op = latest_worker.get("operation") or {}
        res = latest_worker.get("result") or {}
        lines.append("-" * 80)
        lines.append("LATEST WORKER RESULT")
        lines.append("-" * 80)
        lines.append(f"Decision          : {res.get('decision')}")
        lines.append(f"Score             : {res.get('score')}")
        lines.append(f"Job ID            : {op.get('job_id')}")
        lines.append(f"Batch Size        : {op.get('batch_size')}")
        lines.append(f"DB Before         : {op.get('db_before')}")
        lines.append(f"DB After          : {op.get('db_after')}")
        lines.append(f"DB Delta          : {op.get('db_delta')}")
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
    lines.append("199 v3 önce health check yapar; platform READY ise 198 v3 worker execution çağırır.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", type=str, default="worker-1")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    health = run_health_check()
    worker_script, worker_command = build_worker_command(args.worker, args.execute, args.timeout)

    worker_run_result = None
    latest_worker_state_data = None

    if args.execute and worker_command and health.get("decision") == "PLATFORM READY":
        worker_run_result = run_command(worker_command, args.timeout + 120)
        latest_worker_state = latest_file(STATE_DIR, "198_v3_controlled_worker_execution_state_*.json")
        latest_worker_state_data = safe_json(latest_worker_state)

    payload = {
        "module": "199 v3 Orchestrator",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "execute": bool(args.execute),
        "worker": args.worker,
        "timeout": args.timeout,
        "disk_free_gb": disk_free_gb(),
        "health_check": health,
        "worker_script": str(worker_script) if worker_script else None,
        "worker_command": " ".join(worker_command) if worker_command else None,
        "worker_run_result": worker_run_result,
        "latest_worker_state_data": latest_worker_state_data,
    }

    json_path, txt_path = write_outputs(payload)
    result = payload["result"]
    latest_op = (latest_worker_state_data or {}).get("operation") or {}

    print("=" * 80)
    print("199 v3 ORCHESTRATOR TAMAMLANDI")
    print("=" * 80)
    print(f"Execute       : {payload['execute']}")
    print(f"Worker        : {payload['worker']}")
    print(f"Score         : {result['score']} / 100")
    print(f"Decision      : {result['decision']}")
    print(f"Errors        : {len(result['errors'])}")
    print(f"Warnings      : {len(result['warnings'])}")
    print(f"Health        : {health.get('decision')} ({health.get('score')})")
    print(f"Job ID        : {latest_op.get('job_id')}")
    print(f"DB Delta      : {latest_op.get('db_delta')}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
