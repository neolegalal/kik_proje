# -*- coding: utf-8 -*-
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

LAYER_ID = '218'
LAYER_NAME = 'NeoLegal AI Runtime'

COMMANDS = [
    ('218_NeoLegal_AI_Runtime_SDK.py', [sys.executable, str(BASE / ".py" / '218_NeoLegal_AI_Runtime_SDK.py'), '--test']),
    ('218_1_RuntimeController.py', [sys.executable, str(BASE / ".py" / '218_1_RuntimeController.py'), '--run']),
    ('218_2_RagRuntimeEngine.py', [sys.executable, str(BASE / ".py" / '218_2_RagRuntimeEngine.py'), '--run']),
    ('218_3_QueryUnderstanding.py', [sys.executable, str(BASE / ".py" / '218_3_QueryUnderstanding.py'), '--run']),
    ('218_4_LegalAnswerEngine.py', [sys.executable, str(BASE / ".py" / '218_4_LegalAnswerEngine.py'), '--run']),
    ('218_5_CitationEngine.py', [sys.executable, str(BASE / ".py" / '218_5_CitationEngine.py'), '--run']),
    ('218_6_HallucinationGuard.py', [sys.executable, str(BASE / ".py" / '218_6_HallucinationGuard.py'), '--run']),
    ('218_7_RuntimeDashboard.py', [sys.executable, str(BASE / ".py" / '218_7_RuntimeDashboard.py'), '--run']),
    ('218_8_RuntimeDecisionEngine.py', [sys.executable, str(BASE / ".py" / '218_8_RuntimeDecisionEngine.py'), '--run']),
    ('218_9_RuntimeAuditor.py', [sys.executable, str(BASE / ".py" / '218_9_RuntimeAuditor.py'), '--run']),
    ('218_10_PublicApiGateway.py', [sys.executable, str(BASE / ".py" / '218_10_PublicApiGateway.py'), '--run']),
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
