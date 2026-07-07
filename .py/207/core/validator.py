# -*- coding: utf-8 -*-
class ExecutionValidator:
    def validate(self, context):
        errors = []
        warnings = []

        if context.get("scheduler_decision") in (None, ""):
            errors.append("Scheduler decision bulunamadı.")

        if context.get("scheduler_decision") == "PAUSE_PRODUCTION":
            errors.append("Scheduler üretimi durdurma kararı vermiş.")

        if context["workers"]["idle_workers"] == 0:
            errors.append("Idle worker yok.")

        if context["queue"]["waiting_jobs"] == 0:
            warnings.append("Waiting job yok.")

        if context["queue"]["selected_jobs"] == 0:
            warnings.append("Seçilecek job sayısı 0.")

        score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
        decision = "EXECUTION CONTEXT READY" if not errors else "EXECUTION CONTEXT BLOCKED"

        return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}
