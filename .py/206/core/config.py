# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

SCHEDULER_DIR = STATE_DIR / "scheduler"
SCHEDULER_HISTORY = SCHEDULER_DIR / "206_scheduler_history.jsonl"
SCHEDULER_SNAPSHOT = SCHEDULER_DIR / "206_scheduler_snapshot.json"
SCHEDULER_DASHBOARD = SCHEDULER_DIR / "206_scheduler_dashboard.json"
SCHEDULER_DECISIONS = SCHEDULER_DIR / "206_scheduler_decisions.jsonl"

QUEUE_FILE = STATE_DIR / "job_queue" / "198_job_queue_state.json"
WORKER_FILE = STATE_DIR / "job_queue" / "198_worker_state.json"
METRICS_FILE = STATE_DIR / "metrics" / "204_metrics_snapshot.json"
INTELLIGENCE_DIR = STATE_DIR / "metrics" / "intelligence"

DEFAULT_BATCH_SIZE = 25
SMALL_BATCH_SIZE = 10
MAX_BATCH_SIZE = 100
MIN_STABILITY_SCORE = 90
