# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1400"
sys.path.insert(0, str(PACKAGE_DIR))
from core.litigation_intelligence_platform_sdk import LitigationIntelligencePlatformSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "litigation_intelligence" / "1409_litigation_probability_updater"
MODULE_ID = "1409"
MODULE_NAME = "Litigation Probability Updater"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--litigation-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = LitigationIntelligencePlatformSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, litigation_type=args.litigation_type, execute=args.execute).run()
    val = res["payload"]["validation"]
    lit = res["payload"]["litigation"]
    decision = "LITIGATION PROBABILITY UPDATER READY" if not val["errors"] else "LITIGATION PROBABILITY UPDATER BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "success_probability": lit["probability"]["success_probability"], "yd_score": lit["stay_of_execution"]["score"], "audit": lit["audit"]["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "1409_litigation_probability_updater.json"
    state = MODULE_DIR / ("1409_litigation_probability_updater_state_" + ts + ".json")
    report = REPORTS / ("1409_litigation_probability_updater_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Probability : " + str(analysis["success_probability"]) + " / 100", "YD Score    : " + str(analysis["yd_score"]) + " / 100", "Audit       : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
