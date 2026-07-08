from pathlib import Path
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
LARGE_SCALE_PRODUCTION_DIR = STATE_DIR / "large_scale_production"
LARGE_SCALE_PRODUCTION_HISTORY = LARGE_SCALE_PRODUCTION_DIR / "217_large_scale_production_history.jsonl"
LARGE_SCALE_PRODUCTION_SNAPSHOT = LARGE_SCALE_PRODUCTION_DIR / "217_large_scale_production_snapshot.json"
LARGE_SCALE_PRODUCTION_DASHBOARD = LARGE_SCALE_PRODUCTION_DIR / "217_large_scale_production_dashboard.json"
CLUSTER_DASHBOARD = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
ENTERPRISE_DASHBOARD = STATE_DIR / "enterprise_platform" / "215_enterprise_platform_dashboard.json"
IMPROVEMENT_DASHBOARD = STATE_DIR / "continuous_improvement" / "214_continuous_improvement_dashboard.json"
