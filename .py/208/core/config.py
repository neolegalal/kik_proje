# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"

AUTOMATION_DIR = STATE_DIR / "automation"
AUTOMATION_HISTORY = AUTOMATION_DIR / "208_automation_history.jsonl"
AUTOMATION_SNAPSHOT = AUTOMATION_DIR / "208_automation_snapshot.json"
AUTOMATION_DASHBOARD = AUTOMATION_DIR / "208_automation_dashboard.json"

EXECUTION_SNAPSHOT = STATE_DIR / "execution" / "207_execution_snapshot.json"
EXECUTION_DASHBOARD = STATE_DIR / "execution" / "207_execution_dashboard.json"
SCHEDULER_DASHBOARD = STATE_DIR / "scheduler" / "206_scheduler_dashboard.json"

SAFE_MODES = ["CONTROLLED", "SMALL_BATCH", "AUTO_SAFE"]
DEFAULT_TRIGGER_MODE = "CONTROLLED"
