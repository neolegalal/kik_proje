# -*- coding: utf-8 -*-
def get_nested(d, path, default=None):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur

class IntelligenceNormalizer:
    def normalize(self, data):
        snapshot = data.get("snapshot") or {}
        dashboard = data.get("dashboard") or {}
        trends = data.get("trends") or {}

        metrics = snapshot.get("metrics", {})
        result = snapshot.get("result", {})

        normalized = {
            "health": {
                "score": result.get("score"),
                "decision": result.get("decision"),
                "errors": len(result.get("errors", [])),
                "warnings": len(result.get("warnings", [])),
            },
            "system": {
                "db_count": get_nested(metrics, ["db", "count"], get_nested(dashboard, ["system", "db_count"], 0)),
                "disk_free_gb": get_nested(metrics, ["disk", "free_gb"], get_nested(dashboard, ["system", "disk_free_gb"], None)),
            },
            "queue": {
                "total": get_nested(metrics, ["queue", "total"], get_nested(dashboard, ["queue", "total"], 0)),
                "waiting": get_nested(metrics, ["queue", "waiting"], get_nested(dashboard, ["queue", "waiting"], 0)),
                "running": get_nested(metrics, ["queue", "running"], get_nested(dashboard, ["queue", "running"], 0)),
                "finished": get_nested(metrics, ["queue", "finished"], get_nested(dashboard, ["queue", "finished"], 0)),
                "failed": get_nested(metrics, ["queue", "failed"], get_nested(dashboard, ["queue", "failed"], 0)),
                "completion_rate": get_nested(metrics, ["queue", "completion_rate"], get_nested(dashboard, ["queue", "completion_rate"], 0)),
            },
            "workers": {
                "total": get_nested(metrics, ["workers", "total"], get_nested(dashboard, ["workers", "total"], 0)),
                "idle": get_nested(metrics, ["workers", "idle"], get_nested(dashboard, ["workers", "idle"], 0)),
                "running": get_nested(metrics, ["workers", "running"], get_nested(dashboard, ["workers", "running"], 0)),
                "jobs_completed": get_nested(metrics, ["workers", "jobs_completed"], get_nested(dashboard, ["workers", "jobs_completed"], 0)),
                "jobs_failed": get_nested(metrics, ["workers", "jobs_failed"], get_nested(dashboard, ["workers", "jobs_failed"], 0)),
            },
            "events": {
                "total": get_nested(metrics, ["events", "total"], get_nested(dashboard, ["events", "total"], 0)),
                "invalid": get_nested(metrics, ["events", "invalid"], get_nested(dashboard, ["events", "invalid"], 0)),
                "by_severity": get_nested(metrics, ["events", "by_severity"], get_nested(dashboard, ["events", "by_severity"], {})),
            },
            "logs": {
                "total": get_nested(metrics, ["logs", "total"], get_nested(dashboard, ["logs", "total"], 0)),
                "invalid": get_nested(metrics, ["logs", "invalid"], get_nested(dashboard, ["logs", "invalid"], 0)),
                "by_level": get_nested(metrics, ["logs", "by_severity"], get_nested(dashboard, ["logs", "by_level"], {})),
            },
            "trends": {
                "db_delta": get_nested(trends, ["trends", "growth", "db_delta"], 0),
                "event_delta": get_nested(trends, ["trends", "growth", "event_delta"], 0),
                "log_delta": get_nested(trends, ["trends", "growth", "log_delta"], 0),
                "queue_finished_delta": get_nested(trends, ["trends", "growth", "queue_finished_delta"], 0),
            }
        }
        return normalized
