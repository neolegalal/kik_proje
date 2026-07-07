# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

METRICS_DIR = STATE_DIR / "metrics"
METRICS_STORE = METRICS_DIR / "204_metrics_snapshot.json"
METRICS_HISTORY = METRICS_DIR / "204_metrics_history.jsonl"

QUEUE_FILE = STATE_DIR / "job_queue" / "198_job_queue_state.json"
WORKER_FILE = STATE_DIR / "job_queue" / "198_worker_state.json"
EVENT_LOG = STATE_DIR / "event_bus" / "201_event_bus.jsonl"
PLATFORM_LOG = STATE_DIR / "logs" / "203_platform.log.jsonl"

MIN_DISK_GB = 50
