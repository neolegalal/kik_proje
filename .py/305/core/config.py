from pathlib import Path
BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NEOLEGAL_KERNEL_DIR = STATE_DIR / "neolegal_kernel"
NEOLEGAL_KERNEL_SNAPSHOT = NEOLEGAL_KERNEL_DIR / "305_neolegal_kernel_snapshot.json"
NEOLEGAL_KERNEL_DASHBOARD = NEOLEGAL_KERNEL_DIR / "305_neolegal_kernel_dashboard.json"
NEOLEGAL_KERNEL_HISTORY = NEOLEGAL_KERNEL_DIR / "305_neolegal_kernel_history.jsonl"
PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"
SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"
TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"
