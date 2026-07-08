from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
LEARNING_DIR = STATE_DIR / "learning"
LEARNING_HISTORY = LEARNING_DIR / "211_learning_history.jsonl"
LEARNING_SNAPSHOT = LEARNING_DIR / "211_learning_snapshot.json"
LEARNING_DASHBOARD = LEARNING_DIR / "211_learning_dashboard.json"
HEALING_SNAPSHOT = STATE_DIR / "self_healing" / "210_healing_snapshot.json"
HEALING_DASHBOARD = STATE_DIR / "self_healing" / "210_healing_dashboard.json"
AUTONOMOUS_DASHBOARD = STATE_DIR / "autonomous" / "209_autonomous_dashboard.json"
AUTOMATION_DASHBOARD = STATE_DIR / "automation" / "208_automation_dashboard.json"
EXECUTION_DASHBOARD = STATE_DIR / "execution" / "207_execution_dashboard.json"
SCHEDULER_DASHBOARD = STATE_DIR / "scheduler" / "206_scheduler_dashboard.json"
