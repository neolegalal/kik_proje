# -*- coding: utf-8 -*-
from config import BASE_DIR, METRICS_SNAPSHOT, METRICS_HISTORY, DASHBOARD_METRICS
from utils import safe_json, read_jsonl, disk_free_gb

def get_nested(d, path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur

def normalize_snapshot(row):
    metrics = row.get("metrics", {})
    result = row.get("result", {})
    return {
        "created_at": row.get("created_at"),
        "score": result.get("score"),
        "decision": result.get("decision"),
        "db_count": get_nested(metrics, ["db", "count"], 0),
        "queue_total": get_nested(metrics, ["queue", "total"], 0),
        "queue_finished": get_nested(metrics, ["queue", "finished"], 0),
        "queue_failed": get_nested(metrics, ["queue", "failed"], 0),
        "queue_completion_rate": get_nested(metrics, ["queue", "completion_rate"], 0),
        "workers_total": get_nested(metrics, ["workers", "total"], 0),
        "workers_idle": get_nested(metrics, ["workers", "idle"], 0),
        "event_total": get_nested(metrics, ["events", "total"], 0),
        "event_invalid": get_nested(metrics, ["events", "invalid"], 0),
        "log_total": get_nested(metrics, ["logs", "total"], 0),
        "log_invalid": get_nested(metrics, ["logs", "invalid"], 0),
        "disk_free_gb": get_nested(metrics, ["disk", "free_gb"], None),
    }

def delta(first, last, key):
    try:
        return (last.get(key) or 0) - (first.get(key) or 0)
    except Exception:
        return None

def build_trends():
    rows, invalid = read_jsonl(METRICS_HISTORY)
    latest_snapshot = safe_json(METRICS_SNAPSHOT)
    dashboard = safe_json(DASHBOARD_METRICS)

    normalized = [normalize_snapshot(x) for x in rows if isinstance(x, dict)]
    if not normalized and latest_snapshot:
        normalized = [normalize_snapshot(latest_snapshot)]

    first = normalized[0] if normalized else {}
    last = normalized[-1] if normalized else {}

    trends = {
        "source": {
            "history_file": str(METRICS_HISTORY),
            "history_rows": len(rows),
            "history_invalid": invalid,
            "has_latest_snapshot": latest_snapshot is not None,
            "has_dashboard_metrics": dashboard is not None,
        },
        "current": last,
        "growth": {
            "db_delta": delta(first, last, "db_count") if len(normalized) >= 2 else 0,
            "event_delta": delta(first, last, "event_total") if len(normalized) >= 2 else 0,
            "log_delta": delta(first, last, "log_total") if len(normalized) >= 2 else 0,
            "queue_finished_delta": delta(first, last, "queue_finished") if len(normalized) >= 2 else 0,
        },
        "quality": {
            "avg_score": round(sum((x.get("score") or 0) for x in normalized) / len(normalized), 2) if normalized else 0,
            "latest_score": last.get("score"),
            "latest_decision": last.get("decision"),
            "event_invalid_latest": last.get("event_invalid"),
            "log_invalid_latest": last.get("log_invalid"),
            "queue_failed_latest": last.get("queue_failed"),
        },
        "series": normalized[-100:],
        "system": {
            "disk_free_gb_now": disk_free_gb(BASE_DIR),
        }
    }
    return trends
