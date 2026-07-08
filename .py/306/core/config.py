from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NEOLEGAL_ENTERPRISE_SERVICES_DIR = STATE_DIR / "neolegal_enterprise_services"
NEOLEGAL_ENTERPRISE_SERVICES_SNAPSHOT = NEOLEGAL_ENTERPRISE_SERVICES_DIR / "306_neolegal_enterprise_services_snapshot.json"
NEOLEGAL_ENTERPRISE_SERVICES_DASHBOARD = NEOLEGAL_ENTERPRISE_SERVICES_DIR / "306_neolegal_enterprise_services_dashboard.json"
NEOLEGAL_ENTERPRISE_SERVICES_HISTORY = NEOLEGAL_ENTERPRISE_SERVICES_DIR / "306_neolegal_enterprise_services_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
