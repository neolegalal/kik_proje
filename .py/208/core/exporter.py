# -*- coding: utf-8 -*-
from .config import AUTOMATION_DIR, AUTOMATION_HISTORY, AUTOMATION_SNAPSHOT, AUTOMATION_DASHBOARD, REPORT_DIR, STATE_DIR
from .utils import ensure_dirs, now_stamp, write_json, append_jsonl

class AutomationExporter:
    def export(self, payload, name="208_0_automation_sdk"):
        ensure_dirs(AUTOMATION_DIR, REPORT_DIR, STATE_DIR)
        ts = now_stamp()
        state = STATE_DIR / f"{name}_state_{ts}.json"
        report = REPORT_DIR / f"{name}_raporu_{ts}.txt"

        write_json(AUTOMATION_SNAPSHOT, payload)
        write_json(state, payload)
        append_jsonl(AUTOMATION_HISTORY, payload)

        dashboard = {
            "automation_status": payload.get("validation", {}).get("decision"),
            "automation_mode": payload.get("plan", {}).get("automation_mode"),
            "trigger_count": len(payload.get("plan", {}).get("triggers", [])),
            "risk": payload.get("context", {}).get("risk"),
            "execution_status": payload.get("context", {}).get("execution_status"),
        }
        write_json(AUTOMATION_DASHBOARD, dashboard)

        lines = [
            "=" * 80,
            "208.0 AUTOMATION SDK",
            "=" * 80,
            "Validation : " + str(payload.get("validation", {}).get("decision")),
            "Score      : " + str(payload.get("validation", {}).get("score")),
            "Mode       : " + str(payload.get("plan", {}).get("automation_mode")),
            "Triggers   : " + str(len(payload.get("plan", {}).get("triggers", []))),
            "",
            "Message:",
            str(payload.get("plan", {}).get("message")),
            "",
            "Dosyalar:",
            str(AUTOMATION_SNAPSHOT),
            str(AUTOMATION_DASHBOARD),
            str(state),
            str(report),
        ]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"snapshot": str(AUTOMATION_SNAPSHOT), "dashboard": str(AUTOMATION_DASHBOARD), "state": str(state), "report": str(report)}
