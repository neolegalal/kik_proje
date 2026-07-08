# -*- coding: utf-8 -*-
def build_dashboard(payload):
    result = payload.get("result", {})
    return {
        "module": "208.8 Notification Automation",
        "score": result.get("score"),
        "decision": result.get("decision"),
        "risk": result.get("risk"),
        "recommendation": result.get("recommendation")
    }
