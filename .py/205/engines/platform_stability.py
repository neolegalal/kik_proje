# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR, TARGET_DB_COUNT
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "stability"
OUT_FILE = ENGINE_DIR / "205_7_stability.json"

class PlatformStabilityEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.7 Platform Stability Index")

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()
        sdk = self.sdk.run()
        n = sdk["payload"]["normalized"]
        analysis = {
            "sdk_score": sdk["payload"]["result"]["score"],
            "queue_failed": n.get("queue", {}).get("failed", 0) or 0,
            "event_invalid": n.get("events", {}).get("invalid", 0) or 0,
            "log_invalid": n.get("logs", {}).get("invalid", 0) or 0,
            "health_errors": n.get("health", {}).get("errors", 0) or 0,
        }
        score = round(clamp(analysis["sdk_score"] - analysis["queue_failed"]*5 - analysis["event_invalid"]*5 - analysis["log_invalid"]*5 - analysis["health_errors"]*10), 2)
        risk = "LOW" if score >= 90 else ("MEDIUM" if score >= 70 else "HIGH")
        decision = "PLATFORM STABILITY READY" if score >= 90 else "PLATFORM STABILITY REVIEW"
        recommendation = "Platform stabil görünüyor; kontrollü üretim sürdürülebilir." if risk == "LOW" else "Platform stability risk nedenleri incelenmelidir."
        summary = "Platform Stability Index: " + str(score) + "/100. Queue failed " + str(analysis["queue_failed"]) + ", event invalid " + str(analysis["event_invalid"]) + ", log invalid " + str(analysis["log_invalid"]) + ", health errors " + str(analysis["health_errors"]) + ". Risk " + risk + ". Öneri: " + recommendation

        result = {"score": score, "decision": decision, "risk": risk, "recommendation": recommendation, "executive_summary": summary}
        payload = {"module": "205.7 Platform Stability Index", "created_at": now_text(), "analysis": analysis, "result": result, "sdk_reference": sdk["paths"]}
        state = STATE_DIR / f"205_7_stability_state_{ts}.json"
        report = REPORT_DIR / f"205_7_stability_raporu_{ts}.txt"
        write_json(OUT_FILE, payload)
        write_json(state, payload)
        report.write_text("\n".join(["="*80, "205.7 Platform Stability Index".upper(), "="*80, "Score    : " + str(score) + " / 100", "Decision : " + str(decision), "Risk     : " + str(risk), "", summary, "", "Dosyalar:", str(OUT_FILE), str(report)]), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUT_FILE), "report": str(report)}}
