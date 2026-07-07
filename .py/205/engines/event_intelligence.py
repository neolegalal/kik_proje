# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "events"
EVENT_FILE = ENGINE_DIR / "205_5_event_intelligence.json"
EVENT_SCORE_FILE = ENGINE_DIR / "205_5_event_score.json"
EVENT_RECOMMENDATION_FILE = ENGINE_DIR / "205_5_event_recommendation.json"
EVENT_SUMMARY_FILE = ENGINE_DIR / "205_5_event_executive_summary.json"


class EventIntelligenceEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.5 Event Intelligence")

    def analyze_events(self, normalized):
        events = normalized.get("events", {})
        trends = normalized.get("trends", {})

        total = events.get("total", 0) or 0
        invalid = events.get("invalid", 0) or 0
        severity = events.get("by_severity", {}) or {}

        info = severity.get("INFO", 0) or 0
        warning = severity.get("WARNING", 0) or 0
        error = severity.get("ERROR", 0) or 0
        critical = severity.get("CRITICAL", 0) or 0
        unknown = severity.get("UNKNOWN", 0) or 0

        event_delta = trends.get("event_delta", 0) or 0

        problem_events = warning + error + critical + invalid
        problem_rate = round((problem_events / total) * 100, 2) if total else 0

        if critical > 0 or error > 0 or invalid > 0:
            event_risk = "HIGH"
        elif warning > 0 or problem_rate > 5:
            event_risk = "MEDIUM"
        else:
            event_risk = "LOW"

        if total == 0:
            density = "NO_EVENTS"
        elif event_delta > 20:
            density = "HIGH"
        elif event_delta > 0:
            density = "NORMAL"
        else:
            density = "STABLE_OR_INSUFFICIENT_HISTORY"

        return {
            "total": total,
            "invalid": invalid,
            "info": info,
            "warning": warning,
            "error": error,
            "critical": critical,
            "unknown": unknown,
            "problem_events": problem_events,
            "problem_rate": problem_rate,
            "event_delta": event_delta,
            "event_density": density,
            "event_risk": event_risk,
            "severity_distribution": severity,
        }

    def calculate_score(self, analysis):
        score = 100

        if analysis["invalid"] > 0:
            score -= min(35, analysis["invalid"] * 15)
        if analysis["critical"] > 0:
            score -= min(45, analysis["critical"] * 20)
        if analysis["error"] > 0:
            score -= min(35, analysis["error"] * 15)
        if analysis["warning"] > 0:
            score -= min(15, analysis["warning"] * 3)
        if analysis["total"] == 0:
            score -= 5

        score = round(clamp(score), 2)

        if score >= 90:
            risk = "LOW"
        elif score >= 70:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "event_score": score,
            "event_risk": risk,
            "event_density": analysis["event_density"],
        }

    def recommendation(self, analysis, score):
        if score["event_risk"] == "HIGH":
            return "Event Bus riskli görünüyor. ERROR/CRITICAL veya invalid event kayıtları incelenmelidir."

        if analysis["warning"] > 0:
            return "Event Bus içinde WARNING olayları var. Kritik değil ancak takip edilmelidir."

        if analysis["total"] == 0:
            return "Event Bus henüz yeterli veri içermiyor. Event Publisher çalıştırılarak veri zenginleştirilebilir."

        return "Event Bus sağlıklı görünüyor. Mevcut event izleme yapısı sürdürülebilir."

    def executive_summary(self, analysis, score, recommendation):
        return (
            f"Event Intelligence sonucuna göre Event Bus skoru {score['event_score']}/100 ve risk seviyesi "
            f"{score['event_risk']} olarak hesaplanmıştır. Toplam {analysis['total']} event içinde "
            f"{analysis['warning']} warning, {analysis['error']} error, {analysis['critical']} critical ve "
            f"{analysis['invalid']} invalid kayıt bulunmaktadır. Problem event oranı %{analysis['problem_rate']} seviyesindedir. "
            f"Event yoğunluğu {analysis['event_density']} olarak değerlendirilmiştir. Öneri: {recommendation}"
        )

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()

        sdk_result = self.sdk.run()
        normalized = sdk_result["payload"]["normalized"]

        analysis = self.analyze_events(normalized)
        score = self.calculate_score(analysis)
        rec = self.recommendation(analysis, score)
        summary = self.executive_summary(analysis, score, rec)

        result = {
            "score": score["event_score"],
            "decision": "EVENT INTELLIGENCE READY" if score["event_score"] >= 90 else "EVENT INTELLIGENCE REVIEW",
            "risk": score["event_risk"],
            "recommendation": rec,
            "executive_summary": summary,
        }

        payload = {
            "module": "205.5 Event Intelligence",
            "created_at": now_text(),
            "analysis": analysis,
            "score": score,
            "result": result,
            "sdk_reference": sdk_result["paths"],
        }

        state = STATE_DIR / f"205_5_event_intelligence_state_{ts}.json"
        report = REPORT_DIR / f"205_5_event_intelligence_raporu_{ts}.txt"

        write_json(EVENT_FILE, payload)
        write_json(EVENT_SCORE_FILE, score)
        write_json(EVENT_RECOMMENDATION_FILE, {"recommendation": rec})
        write_json(EVENT_SUMMARY_FILE, {"executive_summary": summary})
        write_json(state, payload)

        lines = [
            "=" * 80,
            "205.5 EVENT INTELLIGENCE",
            "=" * 80,
            f"Score             : {result['score']} / 100",
            f"Decision          : {result['decision']}",
            f"Risk              : {result['risk']}",
            "",
            "EVENTS",
            "-" * 80,
            f"Total             : {analysis['total']}",
            f"Invalid           : {analysis['invalid']}",
            f"INFO              : {analysis['info']}",
            f"WARNING           : {analysis['warning']}",
            f"ERROR             : {analysis['error']}",
            f"CRITICAL          : {analysis['critical']}",
            f"UNKNOWN           : {analysis['unknown']}",
            f"Problem Rate      : {analysis['problem_rate']}%",
            f"Event Delta       : {analysis['event_delta']}",
            f"Event Density     : {analysis['event_density']}",
            "",
            "RECOMMENDATION",
            "-" * 80,
            rec,
            "",
            "EXECUTIVE SUMMARY",
            "-" * 80,
            summary,
            "",
            "Dosyalar:",
            str(EVENT_FILE),
            str(EVENT_SCORE_FILE),
            str(EVENT_RECOMMENDATION_FILE),
            str(EVENT_SUMMARY_FILE),
            str(state),
            str(report),
        ]

        report.write_text("\\n".join(lines), encoding="utf-8")

        return {
            "payload": payload,
            "result": result,
            "paths": {
                "event": str(EVENT_FILE),
                "score": str(EVENT_SCORE_FILE),
                "recommendation": str(EVENT_RECOMMENDATION_FILE),
                "summary": str(EVENT_SUMMARY_FILE),
                "state": str(state),
                "report": str(report),
            }
        }
