from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NEOLEGAL_API_GATEWAY_DIR = STATE_DIR / "neolegal_api_gateway"
NEOLEGAL_API_GATEWAY_SNAPSHOT = NEOLEGAL_API_GATEWAY_DIR / "308_neolegal_api_gateway_snapshot.json"
NEOLEGAL_API_GATEWAY_DASHBOARD = NEOLEGAL_API_GATEWAY_DIR / "308_neolegal_api_gateway_dashboard.json"
NEOLEGAL_API_GATEWAY_HISTORY = NEOLEGAL_API_GATEWAY_DIR / "308_neolegal_api_gateway_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
