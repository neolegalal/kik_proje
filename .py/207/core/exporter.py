# -*- coding: utf-8 -*-
from .config import EXECUTION_DIR, EXECUTION_HISTORY, EXECUTION_SNAPSHOT, EXECUTION_DASHBOARD, REPORT_DIR, STATE_DIR
from .utils import ensure_dirs, now_stamp, write_json, append_jsonl

class ExecutionExporter:
    def export(self, payload, name="207_0_execution_sdk"):
        ensure_dirs(EXECUTION_DIR, REPORT_DIR, STATE_DIR)
        ts = now_stamp()
        state = STATE_DIR / f"{name}_state_{ts}.json"
        report = REPORT_DIR / f"{name}_raporu_{ts}.txt"

        write_json(EXECUTION_SNAPSHOT, payload)
        write_json(state, payload)
        append_jsonl(EXECUTION_HISTORY, payload)

        dashboard = {
            "execution_status": payload.get("validation", {}).get("decision"),
            "execution_mode": payload.get("plan", {}).get("execution_mode"),
            "assignment_count": len(payload.get("plan", {}).get("assignments", [])),
            "risk": payload.get("context", {}).get("scheduler_risk"),
            "scheduler_decision": payload.get("context", {}).get("scheduler_decision"),
        }
        write_json(EXECUTION_DASHBOARD, dashboard)

        lines = [
            "=" * 80,
            "207.0 EXECUTION SDK",
            "=" * 80,
            "Validation : " + str(payload.get("validation", {}).get("decision")),
            "Score      : " + str(payload.get("validation", {}).get("score")),
            "Mode       : " + str(payload.get("plan", {}).get("execution_mode")),
            "Assignments: " + str(len(payload.get("plan", {}).get("assignments", []))),
            "",
            "Message:",
            str(payload.get("plan", {}).get("message")),
            "",
            "Dosyalar:",
            str(EXECUTION_SNAPSHOT),
            str(EXECUTION_DASHBOARD),
            str(state),
            str(report),
        ]
        report.write_text("\n".join(lines), encoding="utf-8")

        return {"snapshot": str(EXECUTION_SNAPSHOT), "dashboard": str(EXECUTION_DASHBOARD), "state": str(state), "report": str(report)}
