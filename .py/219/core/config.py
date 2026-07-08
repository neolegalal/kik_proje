from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
CLOUD_PLATFORM_DIR = STATE_DIR / "cloud_platform"
CLOUD_PLATFORM_SNAPSHOT = CLOUD_PLATFORM_DIR / "219_cloud_platform_snapshot.json"
CLOUD_PLATFORM_DASHBOARD = CLOUD_PLATFORM_DIR / "219_cloud_platform_dashboard.json"
CLOUD_PLATFORM_HISTORY = CLOUD_PLATFORM_DIR / "219_cloud_platform_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
