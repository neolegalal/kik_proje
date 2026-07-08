# -*- coding: utf-8 -*-
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

LAYER_ID = '215'
LAYER_NAME = 'Enterprise Platform'

COMMANDS = [
    ('215_Enterprise_Platform_SDK.py', [sys.executable, str(BASE / ".py" / '215_Enterprise_Platform_SDK.py'), '--test']),
    ('215_1_EnterpriseController.py', [sys.executable, str(BASE / ".py" / '215_1_EnterpriseController.py'), '--run']),
    ('215_2_TenantManager.py', [sys.executable, str(BASE / ".py" / '215_2_TenantManager.py'), '--run']),
    ('215_3_AccessGovernance.py', [sys.executable, str(BASE / ".py" / '215_3_AccessGovernance.py'), '--run']),
    ('215_4_PolicyRegistry.py', [sys.executable, str(BASE / ".py" / '215_4_PolicyRegistry.py'), '--run']),
    ('215_5_ServiceCatalog.py', [sys.executable, str(BASE / ".py" / '215_5_ServiceCatalog.py'), '--run']),
    ('215_6_ComplianceManager.py', [sys.executable, str(BASE / ".py" / '215_6_ComplianceManager.py'), '--run']),
    ('215_7_EnterpriseDashboard.py', [sys.executable, str(BASE / ".py" / '215_7_EnterpriseDashboard.py'), '--run']),
    ('215_8_EnterpriseDecisionEngine.py', [sys.executable, str(BASE / ".py" / '215_8_EnterpriseDecisionEngine.py'), '--run']),
    ('215_9_EnterpriseAuditor.py', [sys.executable, str(BASE / ".py" / '215_9_EnterpriseAuditor.py'), '--run']),
    ('215_10_EnterpriseReleaseManager.py', [sys.executable, str(BASE / ".py" / '215_10_EnterpriseReleaseManager.py'), '--run']),
]

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    print("=" * 80)
    print(str(LAYER_ID) + " " + LAYER_NAME.upper() + " RUN ALL BASLADI")
    print("=" * 80)
    passed = 0
    failed = 0
    failed_modules = []
    for module_name, cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode == 0:
            passed += 1
        else:
            failed += 1
            failed_modules.append(module_name)
    total = len(COMMANDS)
    score = round((passed / total) * 100, 2) if total else 0
    decision = "PASS" if failed == 0 else "FAIL"
    ready = "YES" if failed == 0 else "NO"
    summary = {"created_at": now_text(), "layer_id": LAYER_ID, "layer_name": LAYER_NAME, "modules": total, "passed": passed, "failed": failed, "failed_modules": failed_modules, "production_score": score, "final_decision": decision, "production_ready": ready}
    summary_path = SUMMARY_DIR / (str(LAYER_ID) + "_production_summary.json")
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("FINAL PRODUCTION SUMMARY")
    print("=" * 80)
    print("Layer             : " + str(LAYER_ID) + " " + LAYER_NAME)
    print("Modules           : " + str(total))
    print("Passed            : " + str(passed))
    print("Failed            : " + str(failed))
    print("Production Score  : " + str(score) + " / 100")
    print("FINAL DECISION    : " + decision)
    print("Production Ready  : " + ready)
    if failed_modules:
        print("")
        print("Failed Modules")
        for item in failed_modules:
            print("- " + item)
    print("")
    print("Summary JSON:")
    print(summary_path)
    print("=" * 80)
    sys.exit(0 if decision == "PASS" else 1)

if __name__ == "__main__":
    main()
