# -*- coding: utf-8 -*-
from registry import run as run_registry
from history import append_history
from utils import now_text

def plan():
    reg = run_registry(init=False)
    jobs = reg["registry"].get("jobs", [])
    enabled_jobs = [j for j in jobs if j.get("enabled") is True]
    result = {
        "score": 100 if reg["result"]["decision"] == "SCHEDULER REGISTRY READY" else 85,
        "decision": "SCHEDULER PLAN READY",
        "errors": [],
        "warnings": [],
    }
    return {"jobs": jobs, "enabled_jobs": enabled_jobs, "registry_result": reg["result"], "result": result}

def record_plan():
    p = plan()
    append_history({
        "event": "SchedulerPlanCreated",
        "status": "PASS",
        "enabled_jobs": len(p["enabled_jobs"]),
        "total_jobs": len(p["jobs"]),
        "time": now_text(),
    })
    return p
