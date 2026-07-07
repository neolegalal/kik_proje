# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR, TARGET_DB_COUNT
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

ENGINE_DIR = INTELLIGENCE_DIR / "db_growth"
DB_GROWTH_FILE = ENGINE_DIR / "205_4_db_growth_analytics.json"
DB_GROWTH_SCORE_FILE = ENGINE_DIR / "205_4_db_growth_score.json"
DB_GROWTH_FORECAST_FILE = ENGINE_DIR / "205_4_db_growth_forecast.json"
DB_GROWTH_SUMMARY_FILE = ENGINE_DIR / "205_4_db_growth_executive_summary.json"


class DbGrowthAnalyticsEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.4 DB Growth Analytics")

    def analyze_growth(self, normalized):
        system = normalized.get("system", {})
        trends = normalized.get("trends", {})
        queue = normalized.get("queue", {})

        db_count = system.get("db_count", 0) or 0
        db_delta = trends.get("db_delta", 0) or 0
        queue_finished_delta = trends.get("queue_finished_delta", 0) or 0
        queue_finished = queue.get("finished", 0) or 0

        remaining = max(0, TARGET_DB_COUNT - db_count)
        progress_percent = round((db_count / TARGET_DB_COUNT) * 100, 2) if TARGET_DB_COUNT else 0

        if queue_finished_delta > 0:
            growth_per_completed_job = round(db_delta / queue_finished_delta, 2)
            growth_basis = "history_delta"
        elif queue_finished > 0:
            growth_per_completed_job = round(db_count / queue_finished, 2)
            growth_basis = "current_ratio_limited_confidence"
        else:
            growth_per_completed_job = 0
            growth_basis = "insufficient_history"

        if db_delta > 0:
            estimated_cycles_to_target = round(remaining / db_delta, 2)
            forecast_confidence = "MEDIUM"
        else:
            estimated_cycles_to_target = None
            forecast_confidence = "LOW"

        if progress_percent >= 80:
            maturity = "ADVANCED"
        elif progress_percent >= 40:
            maturity = "MID_STAGE"
        elif progress_percent >= 10:
            maturity = "EARLY_GROWTH"
        else:
            maturity = "INITIAL"

        return {
            "target_db_count": TARGET_DB_COUNT,
            "current_db_count": db_count,
            "remaining_to_target": remaining,
            "progress_percent": progress_percent,
            "db_delta": db_delta,
            "queue_finished_delta": queue_finished_delta,
            "growth_per_completed_job": growth_per_completed_job,
            "growth_basis": growth_basis,
            "estimated_cycles_to_target": estimated_cycles_to_target,
            "forecast_confidence": forecast_confidence,
            "maturity_stage": maturity,
        }

    def calculate_score(self, growth):
        score = 100
        if growth["current_db_count"] <= 0:
            score -= 50
        if growth["forecast_confidence"] == "LOW":
            score -= 5
        if growth["db_delta"] == 0:
            score -= 2
        if growth["progress_percent"] >= 10:
            score += 1

        score = round(clamp(score), 2)
        if score >= 90:
            risk = "LOW"
        elif score >= 70:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "db_growth_score": score,
            "db_growth_risk": risk,
            "forecast_confidence": growth["forecast_confidence"],
        }

    def recommendation(self, growth, score):
        if score["db_growth_risk"] == "HIGH":
            return "DB büyüme riski yüksek. Üretim/veritabanı erişimi kontrol edilmelidir."
        if growth["forecast_confidence"] == "LOW":
            return "Forecast güveni düşük. Birkaç yeni production snapshot sonrası tahmin doğruluğu artacaktır."
        if growth["remaining_to_target"] > 0:
            return "DB büyümesi sağlıklı görünüyor. 100.000 karar hedefine yönelik kontrollü üretim sürdürülebilir."
        return "100.000 karar hedefi tamamlanmış görünüyor. Yeni kalite ve güncellik taraması planlanmalıdır."

    def executive_summary(self, growth, score, recommendation):
        eta = growth["estimated_cycles_to_target"]
        eta_text = f"{eta} ölçüm döngüsü" if eta is not None else "henüz güvenilir hesaplanamıyor"
        return (
            f"DB Growth Analytics sonucuna göre veritabanında {growth['current_db_count']} kart bulunmaktadır. "
            f"100.000 kart hedefine kalan miktar {growth['remaining_to_target']} olup ilerleme oranı %{growth['progress_percent']} seviyesindedir. "
            f"DB büyüme skoru {score['db_growth_score']}/100, risk seviyesi {score['db_growth_risk']} olarak hesaplanmıştır. "
            f"Mevcut geçmiş veriye göre hedefe kalan tahmini süre {eta_text}; tahmin güveni {growth['forecast_confidence']} seviyesindedir. "
            f"Öneri: {recommendation}"
        )

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()

        sdk_result = self.sdk.run()
        normalized = sdk_result["payload"]["normalized"]

        growth = self.analyze_growth(normalized)
        score = self.calculate_score(growth)
        rec = self.recommendation(growth, score)
        summary = self.executive_summary(growth, score, rec)

        result = {
            "score": score["db_growth_score"],
            "decision": "DB GROWTH ANALYTICS READY" if score["db_growth_score"] >= 90 else "DB GROWTH ANALYTICS REVIEW",
            "risk": score["db_growth_risk"],
            "recommendation": rec,
            "executive_summary": summary,
        }

        payload = {
            "module": "205.4 DB Growth Analytics",
            "created_at": now_text(),
            "growth": growth,
            "score": score,
            "result": result,
            "sdk_reference": sdk_result["paths"],
        }

        state = STATE_DIR / f"205_4_db_growth_analytics_state_{ts}.json"
        report = REPORT_DIR / f"205_4_db_growth_analytics_raporu_{ts}.txt"

        write_json(DB_GROWTH_FILE, payload)
        write_json(DB_GROWTH_SCORE_FILE, score)
        write_json(DB_GROWTH_FORECAST_FILE, {
            "estimated_cycles_to_target": growth["estimated_cycles_to_target"],
            "forecast_confidence": growth["forecast_confidence"],
            "remaining_to_target": growth["remaining_to_target"],
        })
        write_json(DB_GROWTH_SUMMARY_FILE, {"executive_summary": summary, "recommendation": rec})
        write_json(state, payload)

        lines = [
            "=" * 80,
            "205.4 DB GROWTH ANALYTICS",
            "=" * 80,
            f"Score                 : {result['score']} / 100",
            f"Decision              : {result['decision']}",
            f"Risk                  : {result['risk']}",
            "",
            "DB GROWTH",
            "-" * 80,
            f"Current DB Count      : {growth['current_db_count']}",
            f"Target DB Count       : {growth['target_db_count']}",
            f"Remaining             : {growth['remaining_to_target']}",
            f"Progress              : {growth['progress_percent']}%",
            f"Maturity Stage        : {growth['maturity_stage']}",
            "",
            "VELOCITY / FORECAST",
            "-" * 80,
            f"DB Delta              : {growth['db_delta']}",
            f"Queue Finished Delta  : {growth['queue_finished_delta']}",
            f"Growth / Job          : {growth['growth_per_completed_job']}",
            f"Growth Basis          : {growth['growth_basis']}",
            f"Estimated Cycles      : {growth['estimated_cycles_to_target']}",
            f"Forecast Confidence   : {growth['forecast_confidence']}",
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
            str(DB_GROWTH_FILE),
            str(DB_GROWTH_SCORE_FILE),
            str(DB_GROWTH_FORECAST_FILE),
            str(DB_GROWTH_SUMMARY_FILE),
            str(state),
            str(report),
        ]

        report.write_text("\\n".join(lines), encoding="utf-8")

        return {
            "payload": payload,
            "result": result,
            "paths": {
                "growth": str(DB_GROWTH_FILE),
                "score": str(DB_GROWTH_SCORE_FILE),
                "forecast": str(DB_GROWTH_FORECAST_FILE),
                "summary": str(DB_GROWTH_SUMMARY_FILE),
                "state": str(state),
                "report": str(report),
            }
        }
