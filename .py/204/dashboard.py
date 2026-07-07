# -*- coding: utf-8 -*-
from config import BASE_DIR, STATE_DIR, REPORT_DIR, METRICS_DIR, METRICS_STORE
from utils import now_stamp, now_text, safe_json, write_json, ensure_dirs

DASHBOARD_METRICS_FILE = METRICS_DIR / "204_dashboard_metrics.json"

def load_snapshot():
    return safe_json(METRICS_STORE)

def build_dashboard_data(snapshot):
    if not snapshot:
        return None

    metrics = snapshot.get("metrics", {})
    result = snapshot.get("result", {})

    db = metrics.get("db", {})
    queue = metrics.get("queue", {})
    workers = metrics.get("workers", {})
    events = metrics.get("events", {})
    logs = metrics.get("logs", {})
    disk = metrics.get("disk", {})

    dashboard = {
        "module": "204 v2 Metrics Dashboard Data",
        "generated_at": now_text(),
        "platform_health": {
            "score": result.get("score"),
            "decision": result.get("decision"),
            "errors": len(result.get("errors", [])),
            "warnings": len(result.get("warnings", [])),
        },
        "system": {
            "disk_free_gb": disk.get("free_gb"),
            "disk_status": disk.get("status"),
            "db_status": db.get("status"),
            "db_count": db.get("count"),
            "db_table": db.get("table"),
        },
        "queue": {
            "total": queue.get("total"),
            "waiting": queue.get("waiting"),
            "running": queue.get("running"),
            "finished": queue.get("finished"),
            "failed": queue.get("failed"),
            "retry": queue.get("retry"),
            "completion_rate": queue.get("completion_rate"),
        },
        "workers": {
            "total": workers.get("total"),
            "idle": workers.get("idle"),
            "running": workers.get("running"),
            "disabled": workers.get("disabled"),
            "jobs_completed": workers.get("jobs_completed"),
            "jobs_failed": workers.get("jobs_failed"),
        },
        "events": {
            "total": events.get("total"),
            "invalid": events.get("invalid"),
            "by_type": events.get("by_type"),
            "by_severity": events.get("by_severity"),
        },
        "logs": {
            "total": logs.get("total"),
            "invalid": logs.get("invalid"),
            "by_source": logs.get("by_type"),
            "by_level": logs.get("by_severity"),
        },
        "dashboard_cards": [
            {"title": "DB Cards", "value": db.get("count"), "status": db.get("status")},
            {"title": "Queue Finished", "value": queue.get("finished"), "status": queue.get("status")},
            {"title": "Workers", "value": workers.get("total"), "status": workers.get("status")},
            {"title": "Events", "value": events.get("total"), "status": events.get("status")},
            {"title": "Logs", "value": logs.get("total"), "status": logs.get("status")},
            {"title": "Disk Free GB", "value": disk.get("free_gb"), "status": disk.get("status")},
        ],
    }

    return dashboard

def evaluate(dashboard):
    score = 100
    errors = []
    warnings = []

    if not dashboard:
        return {"score": 0, "decision": "DASHBOARD DATA BLOCKED", "errors": ["Metrics snapshot okunamadı."], "warnings": []}

    if dashboard["platform_health"]["decision"] not in ("METRICS HEALTHY", "METRICS REVIEW"):
        score -= 20
        warnings.append("Metrics snapshot sağlıklı görünmüyor.")

    if dashboard["system"]["db_count"] is None:
        score -= 20
        errors.append("DB count yok.")

    if dashboard["queue"]["total"] is None:
        score -= 10
        warnings.append("Queue total yok.")

    if dashboard["workers"]["total"] is None:
        score -= 10
        warnings.append("Worker total yok.")

    if dashboard["events"]["invalid"]:
        score -= min(20, int(dashboard["events"]["invalid"]) * 5)
        warnings.append("Event invalid satırı var.")

    if dashboard["logs"]["invalid"]:
        score -= min(20, int(dashboard["logs"]["invalid"]) * 5)
        warnings.append("Log invalid satırı var.")

    score = max(0, min(100, score))
    decision = "DASHBOARD DATA BLOCKED" if errors else ("DASHBOARD DATA READY" if score >= 95 else "DASHBOARD DATA REVIEW")
    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}

def run():
    ensure_dirs(STATE_DIR, REPORT_DIR, METRICS_DIR)
    ts = now_stamp()
    snapshot = load_snapshot()
    dashboard = build_dashboard_data(snapshot)
    result = evaluate(dashboard)

    state = STATE_DIR / f"204_v2_dashboard_metrics_state_{ts}.json"
    report = REPORT_DIR / f"204_v2_dashboard_metrics_raporu_{ts}.txt"

    payload = {
        "module": "204 v2 Metrics Dashboard Data",
        "created_at": now_text(),
        "source_snapshot": str(METRICS_STORE),
        "dashboard_file": str(DASHBOARD_METRICS_FILE),
        "dashboard": dashboard,
        "result": result,
    }

    write_json(DASHBOARD_METRICS_FILE, dashboard or {})
    write_json(state, payload)

    lines = [
        "="*80,
        "204 v2 METRICS DASHBOARD DATA",
        "="*80,
        f"Score          : {result['score']} / 100",
        f"Decision       : {result['decision']}",
        f"Errors         : {len(result['errors'])}",
        f"Warnings       : {len(result['warnings'])}",
        "",
        "SUMMARY",
        "-"*80,
    ]

    if dashboard:
        lines += [
            f"DB Count       : {dashboard['system']['db_count']}",
            f"Queue Total    : {dashboard['queue']['total']}",
            f"Queue Finished : {dashboard['queue']['finished']}",
            f"Workers Total  : {dashboard['workers']['total']}",
            f"Events Total   : {dashboard['events']['total']}",
            f"Logs Total     : {dashboard['logs']['total']}",
            f"Disk Free      : {dashboard['system']['disk_free_gb']} GB",
        ]
    else:
        lines.append("Dashboard data oluşturulamadı.")

    lines += [
        "",
        "ERRORS",
        "-"*80,
    ]

    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines += ["", "WARNINGS", "-"*80]
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines += [
        "",
        "Dosyalar:",
        str(DASHBOARD_METRICS_FILE),
        str(state),
        str(report),
    ]

    report.write_text("\n".join(lines), encoding="utf-8")
    return {"payload": payload, "result": result, "paths": {"dashboard": str(DASHBOARD_METRICS_FILE), "state": str(state), "report": str(report)}}
