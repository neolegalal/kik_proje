# -*- coding: utf-8 -*-
from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
REGISTRY_DIR = STATE_DIR / "service_registry"
JOB_QUEUE_DIR = STATE_DIR / "job_queue"
SERVICE_REGISTRY_FILE = REGISTRY_DIR / "199_service_registry.json"
QUEUE_FILE = JOB_QUEUE_DIR / "198_job_queue_state.json"
WORKER_FILE = JOB_QUEUE_DIR / "198_worker_state.json"
MIN_DISK_GB = 50
