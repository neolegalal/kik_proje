# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import TARGET_DB_COUNT, STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

PRODUCTION_DIR = INTELLIGENCE_DIR / "production"
PRODUCTION_ANALYTICS_FILE = PRODUCTION_DIR / "205_1_production_analytics.json"
PRODUCTION_SCORE_FILE = PRODUCTION_DIR / "205_1_production_score.json"
PRODUCTION_FORECAST_FILE = PRODUCTION_DIR / "205_1_production_forecast.json"
PRODUCTION_SUMMARY_FILE = PRODUCTION_DIR / "205_1_production_executive_summary.json"

class ProductionAnalyticsEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.1 Production Analytics Engine")

    def calculate_velocity(self, normalized):
        trends = normalized.get("trends", {})
        queue = normalized.get("queue", {})

        db_delta = trends.get("db_delta", 0) or 0
        queue_finished_delta = trends.get("queue_finished_delta", 0) or 0
        queue_finished = queue.get("finished", 0) or 0

        if queue_finished_delta > 0:
            velocity_per_finished_job = round(db_delta / queue_finished_delta, 2)
        elif queue_finished > 0:
            velocity_per_finished_job = round((normalized.get("system", {}).get("db_count", 0) or 0) / queue_finished, 2)
        else:
            velocity_per_finished_job = 0

        return {
            "db_delta": db_delta,
            "queue_finished_delta": queue_finished_delta,
            "velocity_per_finished_job": velocity_per_finished_job,
            "velocity_basis": "history_delta" if queue_finished_delta > 0 else "current_ratio_or_insufficient_history",
        }

    def calculate_capacity(self, normalized):
        workers = normalized.get("workers", {})
        queue = normalized.get("queue", {})

        total_workers = workers.get("total", 0) or 0
        idle_workers = workers.get("idle", 0) or 0
        running_workers = workers.get("running", 0) or 0
        failed_jobs = queue.get("failed", 0) or 0

        if failed_jobs > 0:
            level = "LOW"
        elif total_workers > 0 and idle_workers == total_workers:
            level = "HIGH"
        elif total_workers > 0 and running_workers > 0:
            level = "MEDIUM"
        else:
            level = "MEDIUM"

        utilization = round((running_workers / total_workers) * 100, 2) if total_workers else 0

        return {
            "capacity_level": level,
            "worker_total": total_workers,
            "worker_idle": idle_workers,
            "worker_running": running_workers,
            "worker_utilization_percent": utilization,
            "queue_failed": failed_jobs,
        }

    def calculate_growth(self, normalized):
        db_count = normalized.get("system", {}).get("db_count", 0) or 0
        remaining = max(0, TARGET_DB_COUNT - db_count)
        progress_percent = round((db_count / TARGET_DB_COUNT) * 100, 2) if TARGET_DB_COUNT else 0
        return {
            "target_db_count": TARGET_DB_COUNT,
            "current_db_count": db_count,
            "remaining_to_target": remaining,
            "progress_percent": progress_percent,
        }

    def calculate_forecast(self, growth, velocity):
        remaining = growth.get("remaining_to_target", 0)
        db_delta = velocity.get("db_delta", 0) or 0

        # Geçmiş yeterli değilse temkinli tahmin.
        if db_delta > 0:
            estimated_cycles_to_target = round(remaining / db_delta, 2)
            confidence = "MEDIUM"
        else:
            estimated_cycles_to_target = None
            confidence = "LOW"

        return {
            "remaining_to_target": remaining,
            "estimated_cycles_to_target": estimated_cycles_to_target,
            "forecast_confidence": confidence,
            "note": "Yeterli zaman serisi oluşmadığında tahmin güveni düşük tutulur.",
        }

    def calculate_production_score(self, normalized, capacity, growth, velocity):
        sdk_score = self.sdk.scoring.global_score(normalized)

        score = sdk_score

        if capacity.get("capacity_level") == "HIGH":
            score += 2
        elif capacity.get("capacity_level") == "LOW":
            score -= 15

        if growth.get("current_db_count", 0) <= 0:
            score -= 20

        if velocity.get("db_delta", 0) == 0:
            # İlk ölçümlerde delta sıfır olabilir; ağır ceza verilmez.
            score -= 2

        score = round(clamp(score), 2)

        if score >= 90:
            risk = "LOW"
        elif score >= 70:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "production_score": score,
            "production_risk": risk,
            "sdk_base_score": sdk_score,
        }

    def recommendation(self, score, capacity, forecast):
        if score.get("production_risk") == "HIGH":
            return "Yeni üretime başlamadan önce production risk nedenleri incelenmelidir."

        if capacity.get("capacity_level") == "HIGH":
            return "Worker kapasitesi uygun görünüyor; kontrollü yeni production batch başlatılabilir."

        if forecast.get("forecast_confidence") == "LOW":
            return "Trend güveni düşük; birkaç yeni metrics snapshot sonrası forecast daha anlamlı hale gelecektir."

        return "Production sağlıklı görünüyor; mevcut üretim planı sürdürülebilir."

    def executive_summary(self, growth, capacity, velocity, forecast, score, recommendation):
        eta = forecast.get("estimated_cycles_to_target")
        eta_text = f"{eta} ölçüm döngüsü" if eta is not None else "henüz güvenilir hesaplanamıyor"

        return (
            f"Production Analytics sonucuna göre veritabanında {growth.get('current_db_count')} kart bulunmaktadır. "
            f"100.000 kart hedefine kalan miktar {growth.get('remaining_to_target')} olup ilerleme oranı %{growth.get('progress_percent')} seviyesindedir. "
            f"Production skoru {score.get('production_score')}/100, risk seviyesi {score.get('production_risk')} olarak hesaplanmıştır. "
            f"Worker kapasitesi {capacity.get('capacity_level')} seviyesindedir ve worker kullanım oranı %{capacity.get('worker_utilization_percent')} olarak görünmektedir. "
            f"Mevcut veriyle 100.000 hedefine tahmini kalan süre {eta_text}. "
            f"Öneri: {recommendation}"
        )

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, PRODUCTION_DIR)
        ts = now_stamp()

        sdk_result = self.sdk.run()
        normalized = sdk_result["payload"]["normalized"]

        velocity = self.calculate_velocity(normalized)
        capacity = self.calculate_capacity(normalized)
        growth = self.calculate_growth(normalized)
        forecast = self.calculate_forecast(growth, velocity)
        score = self.calculate_production_score(normalized, capacity, growth, velocity)
        rec = self.recommendation(score, capacity, forecast)
        summary = self.executive_summary(growth, capacity, velocity, forecast, score, rec)

        result = {
            "score": score["production_score"],
            "decision": "PRODUCTION ANALYTICS READY" if score["production_score"] >= 90 else "PRODUCTION ANALYTICS REVIEW",
            "risk": score["production_risk"],
            "recommendation": rec,
            "executive_summary": summary,
        }

        payload = {
            "module": "205.1 Production Analytics Engine",
            "created_at": now_text(),
            "growth": growth,
            "velocity": velocity,
            "capacity": capacity,
            "forecast": forecast,
            "score": score,
            "result": result,
            "sdk_reference": sdk_result["paths"],
        }

        state = STATE_DIR / f"205_1_production_analytics_state_{ts}.json"
        report = REPORT_DIR / f"205_1_production_analytics_raporu_{ts}.txt"

        write_json(PRODUCTION_ANALYTICS_FILE, payload)
        write_json(PRODUCTION_SCORE_FILE, score)
        write_json(PRODUCTION_FORECAST_FILE, forecast)
        write_json(PRODUCTION_SUMMARY_FILE, {"executive_summary": summary, "recommendation": rec})
        write_json(state, payload)

        lines = [
            "="*80,
            "205.1 PRODUCTION ANALYTICS ENGINE",
            "="*80,
            f"Score                 : {result['score']} / 100",
            f"Decision              : {result['decision']}",
            f"Risk                  : {result['risk']}",
            "",
            "GROWTH",
            "-"*80,
            f"Current DB Count      : {growth['current_db_count']}",
            f"Target DB Count       : {growth['target_db_count']}",
            f"Remaining             : {growth['remaining_to_target']}",
            f"Progress              : {growth['progress_percent']}%",
            "",
            "VELOCITY",
            "-"*80,
            f"DB Delta              : {velocity['db_delta']}",
            f"Queue Finished Delta  : {velocity['queue_finished_delta']}",
            f"Velocity / Job        : {velocity['velocity_per_finished_job']}",
            f"Basis                 : {velocity['velocity_basis']}",
            "",
            "CAPACITY",
            "-"*80,
            f"Capacity Level        : {capacity['capacity_level']}",
            f"Workers Total         : {capacity['worker_total']}",
            f"Workers Idle          : {capacity['worker_idle']}",
            f"Workers Running       : {capacity['worker_running']}",
            f"Utilization           : {capacity['worker_utilization_percent']}%",
            "",
            "FORECAST",
            "-"*80,
            f"Estimated Cycles      : {forecast['estimated_cycles_to_target']}",
            f"Confidence            : {forecast['forecast_confidence']}",
            "",
            "RECOMMENDATION",
            "-"*80,
            rec,
            "",
            "EXECUTIVE SUMMARY",
            "-"*80,
            summary,
            "",
            "Dosyalar:",
            str(PRODUCTION_ANALYTICS_FILE),
            str(PRODUCTION_SCORE_FILE),
            str(PRODUCTION_FORECAST_FILE),
            str(PRODUCTION_SUMMARY_FILE),
            str(state),
            str(report),
        ]

        report.write_text("\n".join(lines), encoding="utf-8")

        return {
            "payload": payload,
            "result": result,
            "paths": {
                "analytics": str(PRODUCTION_ANALYTICS_FILE),
                "score": str(PRODUCTION_SCORE_FILE),
                "forecast": str(PRODUCTION_FORECAST_FILE),
                "summary": str(PRODUCTION_SUMMARY_FILE),
                "state": str(state),
                "report": str(report),
            }
        }
