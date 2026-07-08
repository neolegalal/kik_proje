from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
AUDIT_INTELLIGENCE_DIR = STATE_DIR / "audit_intelligence"
AUDIT_INTELLIGENCE_SNAPSHOT = AUDIT_INTELLIGENCE_DIR / "304_audit_intelligence_snapshot.json"
AUDIT_INTELLIGENCE_DASHBOARD = AUDIT_INTELLIGENCE_DIR / "304_audit_intelligence_dashboard.json"
AUDIT_INTELLIGENCE_HISTORY = AUDIT_INTELLIGENCE_DIR / "304_audit_intelligence_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
