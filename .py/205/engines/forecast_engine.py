# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR, TARGET_DB_COUNT
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "forecast"
OUT_FILE = ENGINE_DIR / "205_9_forecast.json"

class ForecastEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.9 Forecast Engine")

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()
        sdk = self.sdk.run()
        n = sdk["payload"]["normalized"]
        db_count = n.get("system", {}).get("db_count", 0) or 0
        db_delta = n.get("trends", {}).get("db_delta", 0) or 0
        remaining = max(0, TARGET_DB_COUNT - db_count)
        eta = round(remaining/db_delta, 2) if db_delta > 0 else None
        analysis = {"target": TARGET_DB_COUNT, "current": db_count, "remaining": remaining, "db_delta": db_delta, "eta_cycles": eta, "confidence": "MEDIUM" if eta is not None else "LOW"}
        score = round(clamp(95 if db_count > 0 else 60), 2)
        if eta is None:
            score = round(clamp(score - 5), 2)
        risk = "LOW" if score >= 90 else ("MEDIUM" if score >= 70 else "HIGH")
        decision = "FORECAST ENGINE READY" if score >= 90 else "FORECAST ENGINE REVIEW"
        recommendation = "Forecast güveni düşük; production sonrası birkaç 204 snapshot alınmalıdır." if eta is None else "Forecast kullanılabilir; üretim planlamasında dikkate alınabilir."
        summary = "Forecast Engine: hedef " + str(TARGET_DB_COUNT) + ", mevcut " + str(db_count) + ", kalan " + str(remaining) + ", db_delta " + str(db_delta) + ", ETA " + str(eta) + ". Öneri: " + recommendation

        result = {"score": score, "decision": decision, "risk": risk, "recommendation": recommendation, "executive_summary": summary}
        payload = {"module": "205.9 Forecast Engine", "created_at": now_text(), "analysis": analysis, "result": result, "sdk_reference": sdk["paths"]}
        state = STATE_DIR / f"205_9_forecast_state_{ts}.json"
        report = REPORT_DIR / f"205_9_forecast_raporu_{ts}.txt"
        write_json(OUT_FILE, payload)
        write_json(state, payload)
        report.write_text("\n".join(["="*80, "205.9 Forecast Engine".upper(), "="*80, "Score    : " + str(score) + " / 100", "Decision : " + str(decision), "Risk     : " + str(risk), "", summary, "", "Dosyalar:", str(OUT_FILE), str(report)]), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUT_FILE), "report": str(report)}}
