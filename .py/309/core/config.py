from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NEOLEGAL_PLATFORM_OS_DIR = STATE_DIR / "neolegal_platform_os"
NEOLEGAL_PLATFORM_OS_SNAPSHOT = NEOLEGAL_PLATFORM_OS_DIR / "309_neolegal_platform_os_snapshot.json"
NEOLEGAL_PLATFORM_OS_DASHBOARD = NEOLEGAL_PLATFORM_OS_DIR / "309_neolegal_platform_os_dashboard.json"
NEOLEGAL_PLATFORM_OS_HISTORY = NEOLEGAL_PLATFORM_OS_DIR / "309_neolegal_platform_os_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
