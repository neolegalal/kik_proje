# -*- coding: utf-8 -*-
from core.sdk import AutonomousSDK
from core.config import STATE_DIR, REPORT_DIR, AUTONOMOUS_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json

MODULE_DIR = AUTONOMOUS_DIR / "209_10_operations_auditor"
OUTPUT_FILE = MODULE_DIR / "209_10_operations_auditor.json"

class OperationsAuditorModule:
    def __init__(self):
        self.sdk = AutonomousSDK(name="209.10 Operations Auditor")

    def analyze(self, context, plan):
        return {
            "module_id": "209.10",
            "module_name": "Operations Auditor",
            "status": "SKELETON_READY",
            "context": context,
            "plan": plan
        }

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR)
        ts = now_stamp()
        sdk_result = self.sdk.run()
        context = sdk_result["payload"]["context"]
        plan = sdk_result["payload"]["plan"]
        validation = sdk_result["payload"]["validation"]
        analysis = self.analyze(context, plan)

        result = {
            "score": validation["score"],
            "decision": "OPERATIONS AUDITOR READY" if not validation["errors"] else "OPERATIONS AUDITOR REVIEW",
            "risk": context.get("risk"),
            "recommendation": plan.get("message")
        }

        payload = {
            "module": "209.10 Operations Auditor",
            "created_at": now_text(),
            "analysis": analysis,
            "result": result,
            "sdk_reference": sdk_result["paths"]
        }

        state = STATE_DIR / f"209_10_operations_auditor_state_{ts}.json"
        report = REPORT_DIR / f"209_10_operations_auditor_raporu_{ts}.txt"

        write_json(OUTPUT_FILE, payload)
        write_json(state, payload)

        lines = [
            "=" * 80,
            "209.10 Operations Auditor".upper(),
            "=" * 80,
            "Score    : " + str(result["score"]) + " / 100",
            "Decision : " + str(result["decision"]),
            "Risk     : " + str(result["risk"]),
            "",
            "Recommendation:",
            str(result["recommendation"]),
            "",
            "Dosyalar:",
            str(OUTPUT_FILE),
            str(state),
            str(report)
        ]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUTPUT_FILE), "state": str(state), "report": str(report)}}
