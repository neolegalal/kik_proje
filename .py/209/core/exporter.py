# -*- coding: utf-8 -*-
from .config import AUTONOMOUS_DIR, AUTONOMOUS_HISTORY, AUTONOMOUS_SNAPSHOT, AUTONOMOUS_DASHBOARD, REPORT_DIR, STATE_DIR
from .utils import ensure_dirs, now_stamp, write_json, append_jsonl

class AutonomousExporter:
    def export(self, payload, name="209_0_autonomous_sdk"):
        ensure_dirs(AUTONOMOUS_DIR, REPORT_DIR, STATE_DIR)
        ts = now_stamp()
        state = STATE_DIR / f"{name}_state_{ts}.json"
        report = REPORT_DIR / f"{name}_raporu_{ts}.txt"

        write_json(AUTONOMOUS_SNAPSHOT, payload)
        write_json(state, payload)
        append_jsonl(AUTONOMOUS_HISTORY, payload)

        dashboard = {
            "autonomous_status": payload.get("validation", {}).get("decision"),
            "operation_mode": payload.get("plan", {}).get("operation_mode"),
            "operation_count": len(payload.get("plan", {}).get("operations", [])),
            "risk": payload.get("context", {}).get("risk"),
            "automation_status": payload.get("context", {}).get("automation_status"),
        }
        write_json(AUTONOMOUS_DASHBOARD, dashboard)

        lines = [
            "=" * 80,
            "209.0 AUTONOMOUS OPERATIONS SDK",
            "=" * 80,
            "Validation : " + str(payload.get("validation", {}).get("decision")),
            "Score      : " + str(payload.get("validation", {}).get("score")),
            "Mode       : " + str(payload.get("plan", {}).get("operation_mode")),
            "Operations : " + str(len(payload.get("plan", {}).get("operations", []))),
            "",
            "Message:",
            str(payload.get("plan", {}).get("message")),
            "",
            "Dosyalar:",
            str(AUTONOMOUS_SNAPSHOT),
            str(AUTONOMOUS_DASHBOARD),
            str(state),
            str(report),
        ]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"snapshot": str(AUTONOMOUS_SNAPSHOT), "dashboard": str(AUTONOMOUS_DASHBOARD), "state": str(state), "report": str(report)}
