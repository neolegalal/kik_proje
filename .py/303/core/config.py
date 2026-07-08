from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
SECURITY_GOVERNANCE_DIR = STATE_DIR / "security_governance"
SECURITY_GOVERNANCE_SNAPSHOT = SECURITY_GOVERNANCE_DIR / "303_security_governance_snapshot.json"
SECURITY_GOVERNANCE_DASHBOARD = SECURITY_GOVERNANCE_DIR / "303_security_governance_dashboard.json"
SECURITY_GOVERNANCE_HISTORY = SECURITY_GOVERNANCE_DIR / "303_security_governance_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
