# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "2050"
sys.path.insert(0, str(PACKAGE_DIR))
from core.validation_benchmark_platform_sdk import ValidationBenchmarkPlatformSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "validation_benchmark_platform" / "2053_accuracy_analyzer"
MODULE_ID = "2053"
MODULE_NAME = "Accuracy Analyzer"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold-standard", default=None)
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = ValidationBenchmarkPlatformSDK(name=MODULE_ID + " " + MODULE_NAME, gold_standard_path=args.gold_standard, master_record_path=args.master_record, execute=args.execute).run()
    val = res["payload"]["validation"]
    acc = res["payload"]["accuracy"]
    hall = res["payload"]["hallucination"]
    cons = res["payload"]["consistency"]
    audit = res["payload"]["audit"]
    decision = "ACCURACY ANALYZER READY" if not val["errors"] else "ACCURACY ANALYZER BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "accuracy": acc["accuracy"], "main_issue_detection": acc["main_issue_detection"], "citation_accuracy": acc["citation_accuracy"], "hallucination_rate": hall["hallucination_rate"], "consistency": cons["consistency_score"], "audit": audit["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "2053_accuracy_analyzer.json"
    state = MODULE_DIR / ("2053_accuracy_analyzer_state_" + ts + ".json")
    report = REPORTS / ("2053_accuracy_analyzer_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score              : " + str(analysis["score"]) + " / 100", "Decision           : " + str(analysis["decision"]), "Accuracy           : " + str(analysis["accuracy"]) + " / 100", "Main Issue         : " + str(analysis["main_issue_detection"]) + " / 100", "Citation Accuracy  : " + str(analysis["citation_accuracy"]) + " / 100", "Hallucination      : " + str(analysis["hallucination_rate"]) + " / 100", "Consistency        : " + str(analysis["consistency"]) + " / 100", "Audit              : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
