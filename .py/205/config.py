# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

METRICS_DIR = STATE_DIR / "metrics"
METRICS_SNAPSHOT = METRICS_DIR / "204_metrics_snapshot.json"
METRICS_HISTORY = METRICS_DIR / "204_metrics_history.jsonl"
DASHBOARD_METRICS = METRICS_DIR / "204_dashboard_metrics.json"

TREND_DIR = METRICS_DIR / "trends"
TREND_FILE = TREND_DIR / "205_metrics_trends.json"
TREND_HISTORY = TREND_DIR / "205_metrics_trend_history.jsonl"
