# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
SCHEDULER_DIR = STATE_DIR / "scheduler"

SCHEDULER_REGISTRY_FILE = SCHEDULER_DIR / "202_scheduler_registry.json"
SCHEDULER_HISTORY_FILE = SCHEDULER_DIR / "202_scheduler_history.jsonl"

PLATFORM_CORE = PY_DIR / "200_Platform.py"
EVENT_BUS = PY_DIR / "201_v1_Event_Bus.py"
EVENT_PUBLISHER = PY_DIR / "201_v2_Event_Publisher_Integration.py"
EVENT_AUDITOR = PY_DIR / "201_v3_Event_Bus_Viewer_Auditor.py"

DEFAULT_JOBS = [
    {
        "job_id": "SCHED-HEALTH-DAILY",
        "name": "Daily Platform Health",
        "enabled": True,
        "schedule": "daily",
        "action": "platform_health",
        "command": 'python ".py\\200_Platform.py" --status',
        "priority": 1,
        "notes": "Platform sağlık kontrolü."
    },
    {
        "job_id": "SCHED-EVENT-PUBLISH",
        "name": "Event Publisher",
        "enabled": True,
        "schedule": "manual",
        "action": "event_publish",
        "command": 'python ".py\\201_v2_Event_Publisher_Integration.py" --publish',
        "priority": 2,
        "notes": "Son state dosyalarını Event Bus'a işler."
    },
    {
        "job_id": "SCHED-EVENT-AUDIT",
        "name": "Event Audit",
        "enabled": True,
        "schedule": "manual",
        "action": "event_audit",
        "command": 'python ".py\\201_v3_Event_Bus_Viewer_Auditor.py" --tail=20',
        "priority": 3,
        "notes": "Event Bus audit raporu üretir."
    },
    {
        "job_id": "SCHED-RECOVERY-CHECK",
        "name": "Recovery Check",
        "enabled": True,
        "schedule": "manual",
        "action": "recovery_check",
        "command": 'python ".py\\197_v4_Recovery_Manager_Completed_Run_Aware.py"',
        "priority": 4,
        "notes": "Recovery durumunu kontrol eder."
    }
]
