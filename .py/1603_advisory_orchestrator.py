# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1600"
sys.path.insert(0, str(PACKAGE_DIR))
from core.neolegal_expert_orchestrator_sdk import NeoLegalExpertOrchestratorSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "neolegal_expert_orchestrator" / "1603_advisory_orchestrator"
MODULE_ID = "1603"
MODULE_NAME = "Advisory Orchestrator"
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
    parser.add_argument("--expert-mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = NeoLegalExpertOrchestratorSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, expert_mode=args.expert_mode, execute=args.execute).run()
    val = res["payload"]["validation"]
    decision = "ADVISORY ORCHESTRATOR READY" if not val["errors"] else "ADVISORY ORCHESTRATOR BLOCKED"
    analysis = {"success_probability": res["payload"]["expert"]["advisory"]["success_probability"], "risk": res["payload"]["expert"]["advisory"]["risk_level"], "audit": res["payload"]["expert"]["audit"]["status"]}
    analysis["score"] = val["score"]
    analysis["decision"] = decision
    ts = now_stamp()
    output = MODULE_DIR / "1603_advisory_orchestrator.json"
    state = MODULE_DIR / ("1603_advisory_orchestrator_state_" + ts + ".json")
    report = REPORTS / ("1603_advisory_orchestrator_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score    : " + str(analysis["score"]) + " / 100", "Decision : " + str(analysis["decision"])]
    for k, v in analysis.items():
        if k not in ("score", "decision"):
            lines.append(str(k) + " : " + str(v))
    lines += ["", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
