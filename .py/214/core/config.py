from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
CONTINUOUS_IMPROVEMENT_DIR = STATE_DIR / "continuous_improvement"
CONTINUOUS_IMPROVEMENT_HISTORY = CONTINUOUS_IMPROVEMENT_DIR / "214_continuous_improvement_history.jsonl"
CONTINUOUS_IMPROVEMENT_SNAPSHOT = CONTINUOUS_IMPROVEMENT_DIR / "214_continuous_improvement_snapshot.json"
CONTINUOUS_IMPROVEMENT_DASHBOARD = CONTINUOUS_IMPROVEMENT_DIR / "214_continuous_improvement_dashboard.json"
GRAPH_DASHBOARD = STATE_DIR / "knowledge_graph" / "213_knowledge_graph_dashboard.json"
AI_DASHBOARD = STATE_DIR / "ai_orchestrator" / "212_ai_orchestrator_dashboard.json"
LEARNING_DASHBOARD = STATE_DIR / "learning" / "211_learning_dashboard.json"
