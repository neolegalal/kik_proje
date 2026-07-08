# -*- coding: utf-8 -*-
class AutonomousValidator:
    def validate(self, context):
        errors = []
        warnings = []

        if not context.get("automation_status"):
            errors.append("Automation status bulunamadı.")

        if context.get("automation_status") == "AUTOMATION CONTEXT BLOCKED":
            errors.append("Automation context blocked.")

        if context.get("risk") == "HIGH":
            errors.append("Risk HIGH; autonomous operation durdurulmalı.")

        if context.get("trigger_count", 0) <= 0:
            warnings.append("Otonom operasyon için trigger bulunamadı.")

        if not context.get("can_operate_autonomously"):
            warnings.append("Otonom çalışma koşulları tam değil; kontrollü mod önerilir.")

        score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
        decision = "AUTONOMOUS CONTEXT READY" if not errors else "AUTONOMOUS CONTEXT BLOCKED"
        return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}
