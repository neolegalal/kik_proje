# -*- coding: utf-8 -*-
from .utils import now_text

class ExecutionContextBuilder:
    def build(self, raw):
        scheduler_decision = (raw.get("scheduler_snapshot", {}) or {}).get("decision", {})
        dashboard = raw.get("scheduler_dashboard", {}) or {}
        queue_jobs = raw.get("queue", {}).get("jobs", [])
        workers = raw.get("workers", {}).get("workers", [])

        waiting_jobs = [j for j in queue_jobs if j.get("status") == "WAITING"]
        idle_workers = [w for w in workers if w.get("status") in ("IDLE", "idle")]

        return {
            "created_at": now_text(),
            "scheduler_decision": scheduler_decision.get("decision") or dashboard.get("last_decision"),
            "scheduler_risk": scheduler_decision.get("risk") or dashboard.get("risk"),
            "recommended_batch_size": scheduler_decision.get("recommended_batch_size") or dashboard.get("recommended_batch_size") or 0,
            "reason": scheduler_decision.get("reason"),
            "queue": {
                "total_jobs": len(queue_jobs),
                "waiting_jobs": len(waiting_jobs),
                "selected_jobs": min(len(waiting_jobs), scheduler_decision.get("recommended_batch_size") or dashboard.get("recommended_batch_size") or 0),
            },
            "workers": {
                "total_workers": len(workers),
                "idle_workers": len(idle_workers),
                "available_worker_ids": [w.get("worker_id") or w.get("id") or f"worker-{i+1}" for i, w in enumerate(idle_workers)],
            },
        }
