# -*- coding: utf-8 -*-
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

COMMANDS = [
    ('213', 'Knowledge Graph', [sys.executable, str(BASE / ".py" / '213_Run_All.py')]),
    ('214', 'Continuous Improvement', [sys.executable, str(BASE / ".py" / '214_Run_All.py')]),
    ('215', 'Enterprise Platform', [sys.executable, str(BASE / ".py" / '215_Run_All.py')]),
    ('216', 'Production Cluster', [sys.executable, str(BASE / ".py" / '216_Run_All.py')]),
    ('217', 'Large Scale Production', [sys.executable, str(BASE / ".py" / '217_Run_All.py')]),
    ('218', 'NeoLegal AI Runtime', [sys.executable, str(BASE / ".py" / '218_Run_All.py')]),
]

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    print("=" * 80)
    print("213-218 MEGA PLATFORM RUN ALL BASLADI")
    print("=" * 80)
    layer_results = []
    passed = 0
    failed = 0
    for layer_id, layer_name, cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        summary_path = SUMMARY_DIR / (str(layer_id) + "_production_summary.json")
        if summary_path.exists():
            try:
                data = json.loads(summary_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
        else:
            data = {}
        decision = data.get("final_decision")
        if result.returncode == 0 and decision == "PASS":
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        layer_results.append({"layer_id": layer_id, "layer_name": layer_name, "status": status, "returncode": result.returncode, "summary": data})
    total = len(COMMANDS)
    score = round((passed / total) * 100, 2) if total else 0
    decision = "PASS" if failed == 0 else "FAIL"
    ready = "YES" if failed == 0 else "NO"
    platform_summary = {"created_at": now_text(), "layers_total": total, "layers_passed": passed, "layers_failed": failed, "platform_score": score, "final_decision": decision, "platform_ready": ready, "layers": layer_results}
    platform_summary_path = SUMMARY_DIR / "213_218_platform_summary.json"
    platform_summary_path.write_text(json.dumps(platform_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 80)
    print("NEOLEGAL PLATFORM SUMMARY")
    print("=" * 80)
    for item in layer_results:
        print("Layer " + str(item["layer_id"]) + " " + item["layer_name"].ljust(32) + " " + item["status"])
    print("-" * 80)
    print("Layers Passed     : " + str(passed) + " / " + str(total))
    print("Layers Failed     : " + str(failed))
    print("Platform Score    : " + str(score) + " / 100")
    print("FINAL RESULT      : " + decision)
    print("Platform Ready    : " + ready)
    print("")
    print("Summary JSON:")
    print(platform_summary_path)
    print("=" * 80)
    sys.exit(0 if decision == "PASS" else 1)

if __name__ == "__main__":
    main()
