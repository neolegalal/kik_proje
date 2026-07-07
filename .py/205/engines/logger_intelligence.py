# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR, TARGET_DB_COUNT
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "logger"
OUT_FILE = ENGINE_DIR / "205_6_logger.json"

class LoggerIntelligenceEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.6 Logger Intelligence")

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()
        sdk = self.sdk.run()
        n = sdk["payload"]["normalized"]
        logs = n.get("logs", {})
        levels = logs.get("by_level", {}) or {}
        analysis = {"total": logs.get("total", 0) or 0, "invalid": logs.get("invalid", 0) or 0, "levels": levels}
        score = 100 - min(30, analysis["invalid"]*10) - min(20, levels.get("WARNING",0)*3) - min(35, levels.get("ERROR",0)*12) - min(50, levels.get("CRITICAL",0)*20)
        if analysis["total"] == 0:
            score -= 5
        score = round(clamp(score), 2)
        risk = "LOW" if score >= 90 else ("MEDIUM" if score >= 70 else "HIGH")
        decision = "LOGGER INTELLIGENCE READY" if score >= 90 else "LOGGER INTELLIGENCE REVIEW"
        recommendation = "Logger sağlıklı görünüyor. Mevcut log izleme yapısı sürdürülebilir." if risk == "LOW" else "Logger warning/error/invalid kayıtları incelenmelidir."
        summary = "Logger Intelligence: toplam " + str(analysis["total"]) + " log; invalid " + str(analysis["invalid"]) + "; seviyeler " + str(analysis["levels"]) + ". Skor " + str(score) + "/100, risk " + str(risk) + ". Öneri: " + recommendation

        result = {"score": score, "decision": decision, "risk": risk, "recommendation": recommendation, "executive_summary": summary}
        payload = {"module": "205.6 Logger Intelligence", "created_at": now_text(), "analysis": analysis, "result": result, "sdk_reference": sdk["paths"]}
        state = STATE_DIR / f"205_6_logger_state_{ts}.json"
        report = REPORT_DIR / f"205_6_logger_raporu_{ts}.txt"
        write_json(OUT_FILE, payload)
        write_json(state, payload)
        report.write_text("\n".join(["="*80, "205.6 Logger Intelligence".upper(), "="*80, "Score    : " + str(score) + " / 100", "Decision : " + str(decision), "Risk     : " + str(risk), "", summary, "", "Dosyalar:", str(OUT_FILE), str(report)]), encoding="utf-8")
        return {"payload": payload, "result": result, "paths": {"output": str(OUT_FILE), "report": str(report)}}
