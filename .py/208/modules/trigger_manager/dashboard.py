# -*- coding: utf-8 -*-
def build_dashboard(payload):
    result = payload.get("result", {})
    return {
        "module": "208.2 Trigger Manager",
        "score": result.get("score"),
        "decision": result.get("decision"),
        "risk": result.get("risk"),
        "recommendation": result.get("recommendation")
    }
