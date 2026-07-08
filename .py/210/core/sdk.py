# -*- coding: utf-8 -*-
from .config import *
from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl

class SelfHealingSDK:
    def __init__(self, name="210.0 Self-Healing SDK"):
        self.name = name

    def load(self):
        return {
            "autonomous_snapshot": safe_json(AUTONOMOUS_SNAPSHOT),
            "autonomous_dashboard": safe_json(AUTONOMOUS_DASHBOARD),
            "automation_dashboard": safe_json(AUTOMATION_DASHBOARD),
            "execution_dashboard": safe_json(EXECUTION_DASHBOARD),
            "scheduler_dashboard": safe_json(SCHEDULER_DASHBOARD),
        }

    def build_context(self, raw):
        auto_snapshot = raw.get("autonomous_snapshot", {}) or {}
        auto_dashboard = raw.get("autonomous_dashboard", {}) or {}
        automation_dashboard = raw.get("automation_dashboard", {}) or {}
        execution_dashboard = raw.get("execution_dashboard", {}) or {}
        scheduler_dashboard = raw.get("scheduler_dashboard", {}) or {}

        validation = auto_snapshot.get("validation", {}) or {}
        plan = auto_snapshot.get("plan", {}) or {}
        operations = plan.get("operations", []) or []

        risk = auto_dashboard.get("risk") or automation_dashboard.get("risk") or execution_dashboard.get("risk") or scheduler_dashboard.get("risk")
        status = validation.get("decision") or auto_dashboard.get("autonomous_status")
        symptoms = []

        if risk == "HIGH":
            symptoms.append("HIGH_RISK")
        if automation_dashboard.get("automation_status") == "AUTOMATION CONTEXT BLOCKED":
            symptoms.append("AUTOMATION_BLOCKED")
        if execution_dashboard.get("execution_status") == "EXECUTION CONTEXT BLOCKED":
            symptoms.append("EXECUTION_BLOCKED")
        if scheduler_dashboard.get("scheduler_status") == "SCHEDULER CONTEXT BLOCKED":
            symptoms.append("SCHEDULER_BLOCKED")

        return {
            "created_at": now_text(),
            "autonomous_status": status,
            "operation_mode": plan.get("operation_mode") or auto_dashboard.get("operation_mode"),
            "operation_count": len(operations) or auto_dashboard.get("operation_count", 0) or 0,
            "risk": risk,
            "symptoms": symptoms,
            "needs_healing": bool(symptoms),
            "can_self_heal": risk in (None, "LOW") and status == "AUTONOMOUS CONTEXT READY",
        }

    def validate(self, context):
        errors, warnings = [], []
        if not context.get("autonomous_status"):
            warnings.append("Autonomous status bulunamadı.")
        if context.get("risk") == "HIGH":
            errors.append("Risk HIGH; healing manuel doğrulama gerektirir.")
        if context.get("needs_healing") and not context.get("can_self_heal"):
            warnings.append("Healing ihtiyacı var ancak self-heal koşulları tam değil.")
        if context.get("operation_count", 0) <= 0:
            warnings.append("Otonom operasyon kaydı bulunamadı.")

        score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
        decision = "SELF HEALING CONTEXT READY" if not errors else "SELF HEALING CONTEXT BLOCKED"
        return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}

    def plan(self, context, validation):
        if validation["errors"]:
            return {
                "healing_mode": "MANUAL_REVIEW",
                "actions": [{"action": "ESCALATE_TO_MANUAL_REVIEW", "status": "PLANNED"}],
                "message": "Self-healing blocked by validation errors.",
            }

        actions = []
        if context.get("needs_healing"):
            for symptom in context.get("symptoms", []):
                actions.append({"action": "DIAGNOSE_" + symptom, "status": "PLANNED"})
            actions += [
                {"action": "SAFE_REPAIR_ATTEMPT", "status": "PLANNED"},
                {"action": "VERIFY_AFTER_REPAIR", "status": "PLANNED"},
            ]
        else:
            actions += [
                {"action": "NO_HEALING_REQUIRED", "status": "PLANNED"},
                {"action": "CONTINUOUS_MONITORING", "status": "PLANNED"},
            ]
        actions.append({"action": "HEALING_AUDIT_LOG", "status": "PLANNED"})
        return {"healing_mode": "CONTROLLED_SELF_HEALING", "actions": actions, "message": f"{len(actions)} self-healing action planned."}

    def export(self, payload, name="210_0_self_healing_sdk"):
        ensure_dirs(HEALING_DIR, REPORT_DIR, STATE_DIR)
        ts = now_stamp()
        state = STATE_DIR / f"{name}_state_{ts}.json"
        report = REPORT_DIR / f"{name}_raporu_{ts}.txt"
        write_json(HEALING_SNAPSHOT, payload)
        write_json(state, payload)
        append_jsonl(HEALING_HISTORY, payload)
        dashboard = {
            "healing_status": payload.get("validation", {}).get("decision"),
            "healing_mode": payload.get("plan", {}).get("healing_mode"),
            "action_count": len(payload.get("plan", {}).get("actions", [])),
            "risk": payload.get("context", {}).get("risk"),
            "needs_healing": payload.get("context", {}).get("needs_healing"),
        }
        write_json(HEALING_DASHBOARD, dashboard)
        lines = [
            "=" * 80, "210.0 SELF-HEALING SDK", "=" * 80,
            "Validation : " + str(payload.get("validation", {}).get("decision")),
            "Score      : " + str(payload.get("validation", {}).get("score")),
            "Mode       : " + str(payload.get("plan", {}).get("healing_mode")),
            "Actions    : " + str(len(payload.get("plan", {}).get("actions", []))),
            "", "Message:", str(payload.get("plan", {}).get("message")),
            "", "Dosyalar:", str(HEALING_SNAPSHOT), str(HEALING_DASHBOARD), str(state), str(report)
        ]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"snapshot": str(HEALING_SNAPSHOT), "dashboard": str(HEALING_DASHBOARD), "state": str(state), "report": str(report)}

    def run(self):
        raw = self.load()
        context = self.build_context(raw)
        validation = self.validate(context)
        plan = self.plan(context, validation)
        payload = {"module": self.name, "created_at": now_text(), "context": context, "validation": validation, "plan": plan}
        paths = self.export(payload)
        return {"payload": payload, "paths": paths}
