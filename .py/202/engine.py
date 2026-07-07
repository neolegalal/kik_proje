# -*- coding: utf-8 -*-
from config import BASE_DIR, STATE_DIR, REPORT_DIR, SCHEDULER_REGISTRY_FILE
from utils import now_stamp, now_text, ensure_dirs, safe_json, write_json, disk_free_gb
from history import append_history

def load_jobs():
    registry = safe_json(SCHEDULER_REGISTRY_FILE)
    if not registry:
        return None, []
    return registry, registry.get("jobs", [])

def build_execution_plan():
    registry, jobs = load_jobs()
    enabled = [j for j in jobs if j.get("enabled") is True]

    # Öncelik düşük sayı = daha önce çalışır
    enabled.sort(key=lambda j: (int(j.get("priority", 999)), str(j.get("job_id", ""))))

    plan = []
    for order, job in enumerate(enabled, start=1):
        plan.append({
            "order": order,
            "job_id": job.get("job_id"),
            "name": job.get("name"),
            "schedule": job.get("schedule"),
            "action": job.get("action"),
            "command": job.get("command"),
            "priority": job.get("priority"),
            "status": "PLANNED",
        })

    return registry, jobs, plan

def validate_plan(registry, jobs, plan):
    errors = []
    warnings = []

    if registry is None:
        errors.append("Scheduler registry okunamadı.")

    if not jobs:
        errors.append("Scheduler job listesi boş.")

    if not plan:
        warnings.append("Enabled job yok; plan boş.")

    seen = set()
    for item in plan:
        jid = item.get("job_id")
        if jid in seen:
            errors.append(f"Duplicate planned job: {jid}")
        seen.add(jid)

        if not item.get("command"):
            warnings.append(f"{jid}: command boş.")

        if item.get("status") != "PLANNED":
            warnings.append(f"{jid}: beklenmeyen plan status: {item.get('status')}")

    score = 100 - min(60, len(errors) * 15) - min(30, len(warnings) * 3)
    score = max(0, score)

    decision = "SCHEDULER ENGINE BLOCKED" if errors else ("SCHEDULER ENGINE REVIEW" if warnings else "SCHEDULER ENGINE READY")

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
    }

def run(record_history=True):
    ensure_dirs(STATE_DIR, REPORT_DIR)
    ts = now_stamp()
    registry, jobs, plan = build_execution_plan()
    result = validate_plan(registry, jobs, plan)

    payload = {
        "module": "202 v2 Scheduler Engine",
        "created_at": now_text(),
        "disk_free_gb": disk_free_gb(BASE_DIR),
        "registry_file": str(SCHEDULER_REGISTRY_FILE),
        "total_jobs": len(jobs),
        "planned_jobs": len(plan),
        "plan": plan,
        "result": result,
    }

    state = STATE_DIR / f"202_v2_scheduler_engine_state_{ts}.json"
    report = REPORT_DIR / f"202_v2_scheduler_engine_raporu_{ts}.txt"
    write_json(state, payload)

    lines = [
        "=" * 80,
        "202 v2 SCHEDULER ENGINE",
        "=" * 80,
        f"Score        : {result['score']} / 100",
        f"Decision     : {result['decision']}",
        f"Total Jobs   : {len(jobs)}",
        f"Planned Jobs : {len(plan)}",
        "",
        "EXECUTION PLAN",
        "-" * 80,
    ]

    for item in plan:
        lines.append(
            f"{item['order']:02d}. {item.get('job_id'):<24} | "
            f"priority={item.get('priority')} | {item.get('action')} | {item.get('schedule')}"
        )

    lines += [
        "",
        "ERRORS",
        "-" * 80,
    ]
    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines += [
        "",
        "WARNINGS",
        "-" * 80,
    ]
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines += [
        "",
        "NOT:",
        "202 v2 görevleri çalıştırmaz; execution plan oluşturur.",
        "",
        "Dosyalar:",
        str(state),
        str(report),
    ]

    report.write_text("\n".join(lines), encoding="utf-8")

    if record_history:
        append_history({
            "event": "SchedulerExecutionPlanCreated",
            "status": "PASS" if not result["errors"] else "FAIL",
            "decision": result["decision"],
            "score": result["score"],
            "total_jobs": len(jobs),
            "planned_jobs": len(plan),
            "state_file": str(state),
            "report_file": str(report),
        })

    return {
        "payload": payload,
        "result": result,
        "paths": {"state": str(state), "report": str(report)},
    }
