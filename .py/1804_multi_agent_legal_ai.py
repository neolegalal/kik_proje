# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1800"
sys.path.insert(0, str(PACKAGE_DIR))
from core.next_generation_neolegal_sdk import NextGenerationNeoLegalSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "next_generation_neolegal" / "1804_multi_agent_legal_ai"
MODULE_ID = "1804"
MODULE_NAME = "Multi Agent Legal AI"
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
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = NextGenerationNeoLegalSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, mode=args.mode, execute=args.execute).run()
    val = res["payload"]["validation"]
    ng = res["payload"]["next_generation"]
    decision = "MULTI AGENT LEGAL AI READY" if not val["errors"] else "MULTI AGENT LEGAL AI BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "prediction": ng["prediction_engine"]["base_success_probability"], "audit": ng["audit"]["status"], "components_ready": 5}
    ts = now_stamp()
    output = MODULE_DIR / "1804_multi_agent_legal_ai.json"
    state = MODULE_DIR / ("1804_multi_agent_legal_ai_state_" + ts + ".json")
    report = REPORTS / ("1804_multi_agent_legal_ai_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score      : " + str(analysis["score"]) + " / 100", "Decision   : " + str(analysis["decision"]), "Prediction : " + str(analysis["prediction"]) + " / 100", "Audit      : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
