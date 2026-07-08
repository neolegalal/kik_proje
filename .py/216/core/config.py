from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
PRODUCTION_CLUSTER_DIR = STATE_DIR / "production_cluster"
PRODUCTION_CLUSTER_HISTORY = PRODUCTION_CLUSTER_DIR / "216_production_cluster_history.jsonl"
PRODUCTION_CLUSTER_SNAPSHOT = PRODUCTION_CLUSTER_DIR / "216_production_cluster_snapshot.json"
PRODUCTION_CLUSTER_DASHBOARD = PRODUCTION_CLUSTER_DIR / "216_production_cluster_dashboard.json"
ENTERPRISE_DASHBOARD = STATE_DIR / "enterprise_platform" / "215_enterprise_platform_dashboard.json"
IMPROVEMENT_DASHBOARD = STATE_DIR / "continuous_improvement" / "214_continuous_improvement_dashboard.json"
GRAPH_DASHBOARD = STATE_DIR / "knowledge_graph" / "213_knowledge_graph_dashboard.json"
