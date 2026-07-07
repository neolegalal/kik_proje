# -*- coding: utf-8 -*-
def build_report(payload):
    result = payload.get("result", {})
    return "\n".join([
        "207.8 Execution Dashboard",
        "=" * 80,
        "Score: " + str(result.get("score")),
        "Decision: " + str(result.get("decision")),
        "Risk: " + str(result.get("risk"))
    ])
