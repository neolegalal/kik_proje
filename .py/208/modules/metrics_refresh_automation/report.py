# -*- coding: utf-8 -*-
def build_report(payload):
    result = payload.get("result", {})
    return "\\n".join([
        "208.5 Metrics Refresh Automation",
        "=" * 80,
        "Score: " + str(result.get("score")),
        "Decision: " + str(result.get("decision")),
        "Risk: " + str(result.get("risk"))
    ])
