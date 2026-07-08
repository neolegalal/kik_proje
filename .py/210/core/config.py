# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
DOCS_DIR = BASE_DIR / "docs"
RELEASES_DIR = DOCS_DIR / "releases"
CHANGELOG = DOCS_DIR / "CHANGELOG.md"

HEALING_DIR = STATE_DIR / "self_healing"
HEALING_HISTORY = HEALING_DIR / "210_healing_history.jsonl"
HEALING_SNAPSHOT = HEALING_DIR / "210_healing_snapshot.json"
HEALING_DASHBOARD = HEALING_DIR / "210_healing_dashboard.json"

AUTONOMOUS_SNAPSHOT = STATE_DIR / "autonomous" / "209_autonomous_snapshot.json"
AUTONOMOUS_DASHBOARD = STATE_DIR / "autonomous" / "209_autonomous_dashboard.json"
AUTOMATION_DASHBOARD = STATE_DIR / "automation" / "208_automation_dashboard.json"
EXECUTION_DASHBOARD = STATE_DIR / "execution" / "207_execution_dashboard.json"
SCHEDULER_DASHBOARD = STATE_DIR / "scheduler" / "206_scheduler_dashboard.json"
