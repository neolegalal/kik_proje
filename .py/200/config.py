# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
CONFIG_DIR = BASE_DIR / "config"
DOCS_DIR = BASE_DIR / "docs"
DECISIONS_DIR = DOCS_DIR / "decisions"

PLATFORM_CONFIG_FILE = CONFIG_DIR / "neolegal_platform_config.json"
PACKAGE_199_MANAGER = PY_DIR / "199_Package_Manager.py"

MIN_DISK_GB = 50
DEFAULT_TIMEOUT_SECONDS = 3600
