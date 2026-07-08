# -*- coding: utf-8 -*-
from .utils import now_text

class AutomationContextBuilder:
    def build(self, raw):
        execution = raw.get("execution_snapshot", {}) or {}
        execution_dashboard = raw.get("execution_dashboard", {}) or {}
        scheduler_dashboard = raw.get("scheduler_dashboard", {}) or {}

        validation = execution.get("validation", {}) or {}
        plan = execution.get("plan", {}) or {}

        assignments = plan.get("assignments", []) or []
        execution_mode = plan.get("execution_mode") or execution_dashboard.get("execution_mode")

        return {
            "created_at": now_text(),
            "execution_status": validation.get("decision") or execution_dashboard.get("execution_status"),
            "execution_score": validation.get("score"),
            "execution_mode": execution_mode,
            "assignment_count": len(assignments) or execution_dashboard.get("assignment_count", 0) or 0,
            "scheduler_decision": execution_dashboard.get("scheduler_decision") or scheduler_dashboard.get("last_decision"),
            "risk": execution_dashboard.get("risk") or scheduler_dashboard.get("risk"),
            "recommended_batch_size": scheduler_dashboard.get("recommended_batch_size"),
            "can_trigger": execution_mode in ("CONTROLLED", "SMALL_BATCH", "AUTO_SAFE"),
        }
