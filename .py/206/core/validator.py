# -*- coding: utf-8 -*-
class SchedulerValidator:
    def validate(self, context):
        errors = []
        warnings = []
        if context["queue"]["total"] == 0:
            warnings.append("Queue boş veya okunamadı.")
        if context["workers"]["total"] == 0:
            errors.append("Worker bulunamadı.")
        if context["intelligence"]["platform_stability"] is None:
            warnings.append("Platform stability intelligence bulunamadı.")
        score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
        decision = "SCHEDULER CONTEXT READY" if not errors else "SCHEDULER CONTEXT BLOCKED"
        return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}
