# -*- coding: utf-8 -*-
from .config import METRICS_SNAPSHOT, METRICS_HISTORY, DASHBOARD_METRICS, TREND_FILE
from .utils import safe_json, read_jsonl

class IntelligenceDataLoader:
    def load_snapshot(self):
        return safe_json(METRICS_SNAPSHOT)

    def load_history(self):
        rows, invalid = read_jsonl(METRICS_HISTORY)
        return {"rows": rows, "invalid": invalid}

    def load_dashboard(self):
        return safe_json(DASHBOARD_METRICS)

    def load_trends(self):
        return safe_json(TREND_FILE)

    def load_all(self):
        return {
            "snapshot": self.load_snapshot(),
            "history": self.load_history(),
            "dashboard": self.load_dashboard(),
            "trends": self.load_trends(),
        }
