# -*- coding: utf-8 -*-
from .config import QUEUE_FILE, WORKER_FILE, METRICS_FILE, INTELLIGENCE_DIR
from .utils import safe_json

class SchedulerLoader:
    def load_queue(self):
        return safe_json(QUEUE_FILE) or {}

    def load_workers(self):
        return safe_json(WORKER_FILE) or {}

    def load_metrics(self):
        return safe_json(METRICS_FILE) or {}

    def load_intelligence(self):
        files = {
            "production": INTELLIGENCE_DIR / "production" / "205_1_production_analytics.json",
            "queue": INTELLIGENCE_DIR / "queue" / "205_2_queue_intelligence.json",
            "workers": INTELLIGENCE_DIR / "workers" / "205_3_worker_intelligence.json",
            "db_growth": INTELLIGENCE_DIR / "db_growth" / "205_4_db_growth_analytics.json",
            "events": INTELLIGENCE_DIR / "events" / "205_5_event_intelligence.json",
            "logger": INTELLIGENCE_DIR / "logger" / "205_6_logger.json",
            "stability": INTELLIGENCE_DIR / "stability" / "205_7_stability.json",
            "health_trend": INTELLIGENCE_DIR / "health_trend" / "205_8_health_trend.json",
            "forecast": INTELLIGENCE_DIR / "forecast" / "205_9_forecast.json",
            "executive": INTELLIGENCE_DIR / "executive" / "205_10_executive.json",
        }
        return {k: safe_json(p) for k, p in files.items()}

    def load_all(self):
        return {"queue": self.load_queue(), "workers": self.load_workers(), "metrics": self.load_metrics(), "intelligence": self.load_intelligence()}
