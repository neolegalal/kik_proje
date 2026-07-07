# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
LOG_DIR = STATE_DIR / "logs"

PLATFORM_LOG_FILE = LOG_DIR / "203_platform.log.jsonl"
LOGGER_STATE_DIR = STATE_DIR / "logger"

EVENT_LOG_FILE = STATE_DIR / "event_bus" / "201_event_bus.jsonl"

VALID_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
