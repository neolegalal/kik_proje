# -*- coding: utf-8 -*-
class IntelligenceRisk:
    def level(self, score):
        if score >= 90:
            return "LOW"
        if score >= 70:
            return "MEDIUM"
        return "HIGH"

    def reasons(self, normalized):
        reasons = []
        if normalized.get("queue", {}).get("failed", 0):
            reasons.append("Queue içinde failed job var.")
        if normalized.get("events", {}).get("invalid", 0):
            reasons.append("Event log içinde invalid satır var.")
        if normalized.get("logs", {}).get("invalid", 0):
            reasons.append("Logger içinde invalid satır var.")
        if (normalized.get("health", {}).get("errors") or 0) > 0:
            reasons.append("Metrics health errors mevcut.")
        return reasons
