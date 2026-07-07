# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

EXECUTION_DIR = STATE_DIR / "execution"
EXECUTION_HISTORY = EXECUTION_DIR / "207_execution_history.jsonl"
EXECUTION_SNAPSHOT = EXECUTION_DIR / "207_execution_snapshot.json"
EXECUTION_DASHBOARD = EXECUTION_DIR / "207_execution_dashboard.json"

SCHEDULER_SNAPSHOT = STATE_DIR / "scheduler" / "206_scheduler_snapshot.json"
SCHEDULER_DASHBOARD = STATE_DIR / "scheduler" / "206_scheduler_dashboard.json"

QUEUE_FILE = STATE_DIR / "job_queue" / "198_job_queue_state.json"
WORKER_FILE = STATE_DIR / "job_queue" / "198_worker_state.json"

DEFAULT_EXECUTION_MODE = "CONTROLLED"
MAX_PARALLEL_WORKERS = 3
