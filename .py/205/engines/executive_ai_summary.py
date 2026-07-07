# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR, TARGET_DB_COUNT
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "executive"
OUT_FILE = ENGINE_DIR / "205_10_executive.json"

class ExecutiveAiSummaryEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.10 Executive AI Summary")

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()
        sdk = self.sdk.run()
        n = sdk["payload"]["normalized"]
        analysis = {"db_count": n.get("system", {}).get("db_count", 0) or 0, "queue": n.get("queue", {}), "workers": n.get("workers", {}), "events": n.get("events", {}), "logs": n.get("logs", {}), "sdk_score": sdk["payload"]["result"]["score"]}
        score = round(clamp(analysis["sdk_score"]), 2)
        risk = "LOW" if score >= 90 else ("MEDIUM" if score >= 70 else "HIGH")
        decision = "EXECUTIVE AI SUMMARY READY" if score >= 90 else "EXECUTIVE AI SUMMARY REVIEW"
        recommendation = "Genel platform durumu sağlıklı. Kontrollü üretim ve metrics snapshot döngüsü sürdürülebilir." if risk == "LOW" else "Genel risk seviyesi takip edilmeli; alt motor raporları incelenmelidir."
        summary = "Executive AI Summary: DB " + str(analysis["db_count"]) + " kart. Queue: " + str(analysis["queue"]) + ". Workers: " + str(analysis["workers"]) + ". Events: " + str(analysis["events"]) + ". Logs: " + str(analysis["logs"]) + ". Genel skor " + str(score) + "/100, risk " + risk + ". Öneri: " + recommendation

        result = {"score": score, "decision": decision, "risk": risk, "recommendation": recommendation, "executive_summary": summary}
        payload = {"module": "205.10 Executive AI Summary", "created_at": now_text(), "analysis": analysis, "result": result, "sdk_reference": sdk["paths"]}
        state = STATE_DIR / f"205_10_executive_state_{ts}.json"
        report = REPORT_DIR / f"205_10_executive_raporu_{ts}.txt"
        write_json(OUT_FILE, payload)
        write_json(state, payload)
        report.write_text("\n".join(["="*80, "205.10 Executive AI Summary".upper(), "="*80, "Score    : " + str(score) + " / 100", "Decision : " + str(decision), "Risk     : " + str(risk), "", summary, "", "Dosyalar:", str(OUT_FILE), str(report)]), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUT_FILE), "report": str(report)}}
