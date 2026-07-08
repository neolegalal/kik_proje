from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
KNOWLEDGE_GRAPH_DIR = STATE_DIR / "knowledge_graph"
KNOWLEDGE_GRAPH_HISTORY = KNOWLEDGE_GRAPH_DIR / "213_knowledge_graph_history.jsonl"
KNOWLEDGE_GRAPH_SNAPSHOT = KNOWLEDGE_GRAPH_DIR / "213_knowledge_graph_snapshot.json"
KNOWLEDGE_GRAPH_DASHBOARD = KNOWLEDGE_GRAPH_DIR / "213_knowledge_graph_dashboard.json"
AI_DASHBOARD = STATE_DIR / "ai_orchestrator" / "212_ai_orchestrator_dashboard.json"
LEARNING_DASHBOARD = STATE_DIR / "learning" / "211_learning_dashboard.json"
HEALING_DASHBOARD = STATE_DIR / "self_healing" / "210_healing_dashboard.json"
