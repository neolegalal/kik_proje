# -*- coding: utf-8 -*-
from .utils import now_text

class AutonomousContextBuilder:
    def build(self, raw):
        snapshot = raw.get("automation_snapshot", {}) or {}
        dashboard = raw.get("automation_dashboard", {}) or {}
        validation = snapshot.get("validation", {}) or {}
        plan = snapshot.get("plan", {}) or {}
        triggers = plan.get("triggers", []) or []

        risk = dashboard.get("risk") or snapshot.get("context", {}).get("risk")
        mode = plan.get("automation_mode") or dashboard.get("automation_mode")
        status = validation.get("decision") or dashboard.get("automation_status")

        return {
            "created_at": now_text(),
            "automation_status": status,
            "automation_mode": mode,
            "automation_score": validation.get("score"),
            "risk": risk,
            "trigger_count": len(triggers) or dashboard.get("trigger_count", 0) or 0,
            "can_operate_autonomously": status == "AUTOMATION CONTEXT READY" and risk in (None, "LOW") and (len(triggers) or dashboard.get("trigger_count", 0) or 0) > 0,
        }
