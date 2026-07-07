# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR, TARGET_DB_COUNT
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "health_trend"
OUT_FILE = ENGINE_DIR / "205_8_health_trend.json"

class HealthTrendEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.8 Health Trend Engine")

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()
        sdk = self.sdk.run()
        n = sdk["payload"]["normalized"]
        latest = sdk["payload"]["result"]["score"]
        metrics_score = n.get("health", {}).get("score", 0) or 0
        score = round(clamp((latest + metrics_score) / 2 if metrics_score else latest), 2)
        analysis = {"latest_score": latest, "metrics_score": metrics_score, "latest_decision": sdk["payload"]["result"]["decision"]}
        risk = "LOW" if score >= 90 else ("MEDIUM" if score >= 70 else "HIGH")
        decision = "HEALTH TREND READY" if score >= 90 else "HEALTH TREND REVIEW"
        recommendation = "Health trend sağlıklı görünüyor; mevcut izleme sürdürülebilir." if risk == "LOW" else "Health trend review gerektiriyor."
        summary = "Health Trend: latest SDK score " + str(latest) + ", metrics score " + str(metrics_score) + ", ortalama " + str(score) + "/100. Risk " + risk + ". Öneri: " + recommendation

        result = {"score": score, "decision": decision, "risk": risk, "recommendation": recommendation, "executive_summary": summary}
        payload = {"module": "205.8 Health Trend Engine", "created_at": now_text(), "analysis": analysis, "result": result, "sdk_reference": sdk["paths"]}
        state = STATE_DIR / f"205_8_health_trend_state_{ts}.json"
        report = REPORT_DIR / f"205_8_health_trend_raporu_{ts}.txt"
        write_json(OUT_FILE, payload)
        write_json(state, payload)
        report.write_text("\n".join(["="*80, "205.8 Health Trend Engine".upper(), "="*80, "Score    : " + str(score) + " / 100", "Decision : " + str(decision), "Risk     : " + str(risk), "", summary, "", "Dosyalar:", str(OUT_FILE), str(report)]), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUT_FILE), "report": str(report)}}
