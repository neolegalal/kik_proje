# -*- coding: utf-8 -*-
from core.sdk import SchedulerSDK
from core.config import STATE_DIR, REPORT_DIR, SCHEDULER_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json

MODULE_DIR = SCHEDULER_DIR / "206_4_dependency_resolver"
OUTPUT_FILE = MODULE_DIR / "206_4_dependency_resolver.json"

class DependencyResolverModule:
    def __init__(self):
        self.sdk = SchedulerSDK(name="206.4 Dependency Resolver")

    def analyze(self, context, decision):
        return {
            "module_id": "206.4",
            "module_name": "Dependency Resolver",
            "status": "SKELETON_READY",
            "context": context,
            "decision": decision
        }

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR)
        ts = now_stamp()
        sdk_result = self.sdk.run()
        context = sdk_result["payload"]["context"]
        decision = sdk_result["payload"]["decision"]
        analysis = self.analyze(context, decision)

        result = {
            "score": sdk_result["payload"]["validation"]["score"],
            "decision": "DEPENDENCY RESOLVER READY",
            "risk": decision.get("risk"),
            "recommendation": decision.get("reason")
        }

        payload = {
            "module": "206.4 Dependency Resolver",
            "created_at": now_text(),
            "analysis": analysis,
            "result": result,
            "sdk_reference": sdk_result["paths"]
        }

        state = STATE_DIR / f"206_4_dependency_resolver_state_{ts}.json"
        report = REPORT_DIR / f"206_4_dependency_resolver_raporu_{ts}.txt"

        write_json(OUTPUT_FILE, payload)
        write_json(state, payload)

        lines = [
            "=" * 80,
            "206.4 Dependency Resolver".upper(),
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
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUTPUT_FILE), "state": str(state), "report": str(report)}}
