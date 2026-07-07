# -*- coding: utf-8 -*-
def evaluate(trends):
    score = 100
    errors = []
    warnings = []

    source = trends.get("source", {})
    quality = trends.get("quality", {})
    current = trends.get("current", {})

    if not source.get("has_latest_snapshot"):
        score -= 25
        errors.append("204 metrics snapshot bulunamadı.")

    if source.get("history_rows", 0) == 0:
        score -= 10
        warnings.append("Metrics history boş; trend hesapları sınırlı.")

    if source.get("history_invalid", 0) > 0:
        score -= min(25, source.get("history_invalid") * 5)
        warnings.append("Metrics history içinde bozuk satır var.")

    if not current.get("db_count"):
        score -= 20
        errors.append("Güncel DB count okunamadı.")

    if quality.get("event_invalid_latest", 0):
        score -= 10
        warnings.append("Güncel event invalid satırı var.")

    if quality.get("log_invalid_latest", 0):
        score -= 10
        warnings.append("Güncel log invalid satırı var.")

    if quality.get("queue_failed_latest", 0):
        score -= 10
        warnings.append("Güncel queue failed job var.")

    score = max(0, min(100, score))
    decision = "TRENDS BLOCKED" if errors else ("TRENDS READY" if score >= 90 else "TRENDS REVIEW")
    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}
