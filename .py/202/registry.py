# -*- coding: utf-8 -*-
from config import BASE_DIR, STATE_DIR, REPORT_DIR, SCHEDULER_DIR, SCHEDULER_REGISTRY_FILE, DEFAULT_JOBS
from utils import now_text, now_stamp, ensure_dirs, write_json, safe_json, disk_free_gb

def load_registry():
    data = safe_json(SCHEDULER_REGISTRY_FILE)
    if data:
        return data, False
    return create_registry()

def create_registry():
    ensure_dirs(STATE_DIR, REPORT_DIR, SCHEDULER_DIR)
    registry = {
        "module": "202 Platform Scheduler Registry",
        "created_at": now_text(),
        "updated_at": now_text(),
        "version": "v1",
        "jobs": DEFAULT_JOBS,
    }
    write_json(SCHEDULER_REGISTRY_FILE, registry)
    return registry, True

def validate(registry):
    errors = []
    warnings = []
    jobs = registry.get("jobs", []) if registry else []

    seen = set()
    for job in jobs:
        jid = job.get("job_id")
        if not jid:
            errors.append("job_id eksik görev var.")
            continue
        if jid in seen:
            errors.append(f"Duplicate job_id: {jid}")
        seen.add(jid)

        if job.get("schedule") not in ("manual", "hourly", "daily", "weekly"):
            errors.append(f"{jid}: geçersiz schedule: {job.get('schedule')}")

        if not job.get("command"):
            warnings.append(f"{jid}: command boş.")

        if not isinstance(job.get("enabled"), bool):
            warnings.append(f"{jid}: enabled boolean değil.")

    if not jobs:
        errors.append("Scheduler job registry boş.")

    score = 100 - min(60, len(errors) * 15) - min(30, len(warnings) * 3)
    score = max(0, score)
    decision = "SCHEDULER REGISTRY INVALID" if errors else ("SCHEDULER REGISTRY REVIEW" if warnings else "SCHEDULER REGISTRY READY")
    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}

def run(init=False, force=False):
    ensure_dirs(STATE_DIR, REPORT_DIR, SCHEDULER_DIR)
    ts = now_stamp()

    if init or force or not SCHEDULER_REGISTRY_FILE.exists():
        registry, created = create_registry()
    else:
        registry, created = load_registry()

    result = validate(registry)
    state = STATE_DIR / f"202_pkg_registry_state_{ts}.json"
    report = REPORT_DIR / f"202_pkg_registry_raporu_{ts}.txt"

    payload = {
        "module": "202 Package Scheduler Registry",
        "created_at": now_text(),
        "registry_file": str(SCHEDULER_REGISTRY_FILE),
        "created_now": created,
        "disk_free_gb": disk_free_gb(BASE_DIR),
        "registry": registry,
        "result": result,
    }
    write_json(state, payload)

    jobs = registry.get("jobs", [])
    enabled = sum(1 for j in jobs if j.get("enabled") is True)
    report.write_text("\n".join([
        "="*80,
        "202 PACKAGE - SCHEDULER REGISTRY",
        "="*80,
        f"Score      : {result['score']} / 100",
        f"Decision   : {result['decision']}",
        f"Jobs       : {len(jobs)}",
        f"Enabled    : {enabled}",
        f"Created    : {created}",
        "",
        "JOBS",
        "-"*80,
        *[f"{j.get('job_id'):<24} | {j.get('schedule'):<8} | enabled={j.get('enabled')} | {j.get('action')}" for j in jobs],
        "",
        "Dosyalar:",
        str(SCHEDULER_REGISTRY_FILE),
        str(state),
        str(report),
    ]), encoding="utf-8")

    return {"registry": registry, "result": result, "paths": {"registry": str(SCHEDULER_REGISTRY_FILE), "state": str(state), "report": str(report)}}
