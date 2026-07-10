
# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1300"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_advisory_intelligence_sdk import LegalAdvisoryIntelligenceSDK

STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "legal_advisory_intelligence" / "1304_precedent_strength_analyzer"
MODULE_ID = "1304"
MODULE_NAME = "Precedent Strength Analyzer"

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
    parser.add_argument("--advisory-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = LegalAdvisoryIntelligenceSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, advisory_type=args.advisory_type, execute=args.execute).run()
    val = res["payload"]["validation"]
    advisory = res["payload"]["advisory"]
    decision = "PRECEDENT STRENGTH ANALYZER READY" if not val["errors"] else "PRECEDENT STRENGTH ANALYZER BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "success_probability": advisory["outcome_probability"]["success_probability"], "court_risk": advisory["court_risk"]["court_risk"], "audit": advisory["audit"]["status"], "recommendation": advisory["strategy"]["recommendation"]}
    ts = now_stamp()
    output = MODULE_DIR / "1304_precedent_strength_analyzer.json"
    state = MODULE_DIR / ("1304_precedent_strength_analyzer_state_" + ts + ".json")
    report = REPORTS / ("1304_precedent_strength_analyzer_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Probability : " + str(analysis["success_probability"]) + " / 100", "Court Risk  : " + str(analysis["court_risk"]), "Audit       : " + str(analysis["audit"]), "", "Recommendation:", str(analysis["recommendation"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)

if __name__ == "__main__":
    main()
