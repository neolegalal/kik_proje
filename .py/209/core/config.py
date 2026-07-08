# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
DOCS_DIR = BASE_DIR / "docs"
RELEASES_DIR = DOCS_DIR / "releases"
CHANGELOG = DOCS_DIR / "CHANGELOG.md"

AUTONOMOUS_DIR = STATE_DIR / "autonomous"
AUTONOMOUS_HISTORY = AUTONOMOUS_DIR / "209_autonomous_history.jsonl"
AUTONOMOUS_SNAPSHOT = AUTONOMOUS_DIR / "209_autonomous_snapshot.json"
AUTONOMOUS_DASHBOARD = AUTONOMOUS_DIR / "209_autonomous_dashboard.json"

AUTOMATION_SNAPSHOT = STATE_DIR / "automation" / "208_automation_snapshot.json"
AUTOMATION_DASHBOARD = STATE_DIR / "automation" / "208_automation_dashboard.json"

DEFAULT_POLICY = "CONTROLLED_AUTONOMY"
MAX_RISK_FOR_AUTO_APPROVAL = "LOW"
