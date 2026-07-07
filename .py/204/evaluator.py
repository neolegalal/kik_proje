# -*- coding: utf-8 -*-
def evaluate(metrics):
    score = 100
    errors = []
    warnings = []

    if metrics["disk"]["status"] == "FAIL":
        score -= 20
        errors.append("Disk alanı kritik seviyede.")

    if metrics["db"]["status"] == "FAIL":
        score -= 25
        errors.append(metrics["db"].get("message", "DB hatası."))

    if metrics["queue"]["status"] == "WARNING":
        score -= 8
        warnings.append(metrics["queue"].get("message", "Queue warning."))

    if metrics["workers"]["status"] == "WARNING":
        score -= 8
        warnings.append(metrics["workers"].get("message", "Worker warning."))

    if metrics["events"]["invalid"] > 0:
        score -= min(20, metrics["events"]["invalid"] * 5)
        warnings.append("Event log içinde bozuk satır var.")

    event_errors = metrics["events"].get("by_severity", {}).get("ERROR", 0) + metrics["events"].get("by_severity", {}).get("CRITICAL", 0)
    if event_errors:
        score -= min(20, event_errors * 3)
        warnings.append(f"Event Bus ERROR/CRITICAL sayısı: {event_errors}")

    if metrics["logs"]["invalid"] > 0:
        score -= min(20, metrics["logs"]["invalid"] * 5)
        warnings.append("Platform log içinde bozuk satır var.")

    log_errors = metrics["logs"].get("by_severity", {}).get("ERROR", 0) + metrics["logs"].get("by_severity", {}).get("CRITICAL", 0)
    if log_errors:
        score -= min(20, log_errors * 3)
        warnings.append(f"Platform Logger ERROR/CRITICAL sayısı: {log_errors}")

    score = max(0, min(100, score))
    decision = "METRICS BLOCKED" if errors else ("METRICS HEALTHY" if score >= 95 else "METRICS REVIEW")

    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}
