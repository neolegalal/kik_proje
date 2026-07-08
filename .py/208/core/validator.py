# -*- coding: utf-8 -*-
class AutomationValidator:
    def validate(self, context):
        errors = []
        warnings = []

        if not context.get("execution_status"):
            errors.append("Execution status bulunamadı.")

        if context.get("execution_status") == "EXECUTION CONTEXT BLOCKED":
            errors.append("Execution context blocked.")

        if context.get("assignment_count", 0) <= 0:
            warnings.append("Automation için assignment bulunamadı.")

        if not context.get("can_trigger"):
            warnings.append("Execution mode otomatik tetikleme için güvenli mod listesinde değil.")

        score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
        decision = "AUTOMATION CONTEXT READY" if not errors else "AUTOMATION CONTEXT BLOCKED"
        return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}
