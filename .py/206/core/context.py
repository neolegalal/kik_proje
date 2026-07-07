# -*- coding: utf-8 -*-
from .utils import now_text

class SchedulerContextBuilder:
    def build(self, raw):
        queue_jobs = raw.get("queue", {}).get("jobs", [])
        workers = raw.get("workers", {}).get("workers", [])
        intelligence = raw.get("intelligence", {})

        def count_jobs(status):
            return sum(1 for j in queue_jobs if j.get("status") == status)

        stability_score = ((intelligence.get("stability") or {}).get("result") or {}).get("score")
        queue_risk = ((intelligence.get("queue") or {}).get("result") or {}).get("risk")
        worker_risk = ((intelligence.get("workers") or {}).get("result") or {}).get("risk")
        forecast_conf = (((intelligence.get("forecast") or {}).get("analysis") or {}).get("confidence"))

        return {
            "created_at": now_text(),
            "queue": {"total": len(queue_jobs), "waiting": count_jobs("WAITING"), "running": count_jobs("RUNNING"), "finished": count_jobs("FINISHED"), "failed": count_jobs("FAILED"), "retry": count_jobs("RETRY")},
            "workers": {"total": len(workers), "idle": sum(1 for w in workers if w.get("status") in ("IDLE", "idle")), "running": sum(1 for w in workers if w.get("status") in ("RUNNING", "running"))},
            "intelligence": {"platform_stability": stability_score, "queue_risk": queue_risk, "worker_risk": worker_risk, "forecast_confidence": forecast_conf},
        }
