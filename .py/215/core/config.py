from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
ENTERPRISE_PLATFORM_DIR = STATE_DIR / "enterprise_platform"
ENTERPRISE_PLATFORM_HISTORY = ENTERPRISE_PLATFORM_DIR / "215_enterprise_platform_history.jsonl"
ENTERPRISE_PLATFORM_SNAPSHOT = ENTERPRISE_PLATFORM_DIR / "215_enterprise_platform_snapshot.json"
ENTERPRISE_PLATFORM_DASHBOARD = ENTERPRISE_PLATFORM_DIR / "215_enterprise_platform_dashboard.json"
IMPROVEMENT_DASHBOARD = STATE_DIR / "continuous_improvement" / "214_continuous_improvement_dashboard.json"
GRAPH_DASHBOARD = STATE_DIR / "knowledge_graph" / "213_knowledge_graph_dashboard.json"
AI_DASHBOARD = STATE_DIR / "ai_orchestrator" / "212_ai_orchestrator_dashboard.json"
