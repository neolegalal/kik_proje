from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NEOLEGAL_AI_RUNTIME_DIR = STATE_DIR / "neolegal_ai_runtime"
NEOLEGAL_AI_RUNTIME_HISTORY = NEOLEGAL_AI_RUNTIME_DIR / "218_neolegal_ai_runtime_history.jsonl"
NEOLEGAL_AI_RUNTIME_SNAPSHOT = NEOLEGAL_AI_RUNTIME_DIR / "218_neolegal_ai_runtime_snapshot.json"
NEOLEGAL_AI_RUNTIME_DASHBOARD = NEOLEGAL_AI_RUNTIME_DIR / "218_neolegal_ai_runtime_dashboard.json"
LARGE_SCALE_DASHBOARD = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
CLUSTER_DASHBOARD = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
AI_DASHBOARD = STATE_DIR / "ai_orchestrator" / "212_ai_orchestrator_dashboard.json"
