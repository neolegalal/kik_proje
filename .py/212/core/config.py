from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
AI_DIR = STATE_DIR / "ai_orchestrator"
AI_HISTORY = AI_DIR / "212_ai_orchestrator_history.jsonl"
AI_SNAPSHOT = AI_DIR / "212_ai_orchestrator_snapshot.json"
AI_DASHBOARD = AI_DIR / "212_ai_orchestrator_dashboard.json"
LEARNING_SNAPSHOT = STATE_DIR / "learning" / "211_learning_snapshot.json"
LEARNING_DASHBOARD = STATE_DIR / "learning" / "211_learning_dashboard.json"
HEALING_DASHBOARD = STATE_DIR / "self_healing" / "210_healing_dashboard.json"
AUTONOMOUS_DASHBOARD = STATE_DIR / "autonomous" / "209_autonomous_dashboard.json"
AUTOMATION_DASHBOARD = STATE_DIR / "automation" / "208_automation_dashboard.json"
EXECUTION_DASHBOARD = STATE_DIR / "execution" / "207_execution_dashboard.json"
DEFAULT_MODELS = ["GPT", "QWEN", "GEMINI", "CLAUDE", "NEOLEGAL_AI"]
