# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

METRICS_DIR = STATE_DIR / "metrics"
INTELLIGENCE_DIR = METRICS_DIR / "intelligence"
INTELLIGENCE_SDK_DIR = INTELLIGENCE_DIR / "sdk"

METRICS_SNAPSHOT = METRICS_DIR / "204_metrics_snapshot.json"
METRICS_HISTORY = METRICS_DIR / "204_metrics_history.jsonl"
DASHBOARD_METRICS = METRICS_DIR / "204_dashboard_metrics.json"
TREND_FILE = METRICS_DIR / "trends" / "205_metrics_trends.json"

SDK_STATUS_FILE = INTELLIGENCE_SDK_DIR / "205_0_sdk_status.json"
SDK_TEST_OUTPUT = INTELLIGENCE_SDK_DIR / "205_0_sdk_test_output.json"

TARGET_DB_COUNT = 100000

RISK_LEVELS = ["LOW", "MEDIUM", "HIGH"]
HEALTH_LEVELS = ["LOW", "MEDIUM", "HIGH"]
