# -*- coding: utf-8 -*-
from .config import DEFAULT_BATCH_SIZE, SMALL_BATCH_SIZE, MIN_STABILITY_SCORE

class SchedulerDecisionHelper:
    def decide(self, context, validation):
        if validation["errors"]:
            return {"decision": "PAUSE_PRODUCTION", "risk": "HIGH", "recommended_batch_size": 0, "reason": "Scheduler context blocked."}
        stability = context["intelligence"].get("platform_stability")
        queue_risk = context["intelligence"].get("queue_risk")
        worker_risk = context["intelligence"].get("worker_risk")
        forecast_conf = context["intelligence"].get("forecast_confidence")
        if stability is not None and stability < MIN_STABILITY_SCORE:
            return {"decision": "PAUSE_PRODUCTION", "risk": "HIGH", "recommended_batch_size": 0, "reason": "Platform stability below safe threshold."}
        if queue_risk == "HIGH" or worker_risk == "HIGH":
            return {"decision": "ALLOW_SMALL_BATCH", "risk": "MEDIUM", "recommended_batch_size": SMALL_BATCH_SIZE, "reason": "Queue or worker risk requires conservative scheduling."}
        if forecast_conf == "LOW":
            return {"decision": "ALLOW_SMALL_BATCH", "risk": "LOW", "recommended_batch_size": SMALL_BATCH_SIZE, "reason": "Forecast confidence is low; controlled batch recommended."}
        return {"decision": "ALLOW_PRODUCTION", "risk": "LOW", "recommended_batch_size": DEFAULT_BATCH_SIZE, "reason": "Scheduler context healthy."}
