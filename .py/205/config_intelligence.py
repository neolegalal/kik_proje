# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

METRICS_DIR = STATE_DIR / "metrics"
TREND_DIR = METRICS_DIR / "trends"
INTELLIGENCE_DIR = METRICS_DIR / "intelligence"

METRICS_SNAPSHOT = METRICS_DIR / "204_metrics_snapshot.json"
METRICS_HISTORY = METRICS_DIR / "204_metrics_history.jsonl"
DASHBOARD_METRICS = METRICS_DIR / "204_dashboard_metrics.json"
TREND_FILE = TREND_DIR / "205_metrics_trends.json"

INTELLIGENCE_SCHEMA_FILE = INTELLIGENCE_DIR / "205_v2_intelligence_schema.json"
INTELLIGENCE_CONTRACT_FILE = INTELLIGENCE_DIR / "205_v2_engine_contracts.json"
INTELLIGENCE_OUTPUT_FILE = INTELLIGENCE_DIR / "205_v2_intelligence_framework.json"

TARGET_DB_COUNT = 100000
MIN_STABILITY_SCORE = 90
