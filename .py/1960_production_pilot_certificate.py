# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1950"
sys.path.insert(0, str(PACKAGE_DIR))
from core.unified_decision_processor_sdk import UnifiedDecisionProcessorSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "unified_decision_processor" / "1960_production_pilot_certificate"
MODULE_ID = "1960"
MODULE_NAME = "Production Pilot Certificate"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-text", default=None)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = UnifiedDecisionProcessorSDK(name=MODULE_ID + " " + MODULE_NAME, decision_text=args.decision_text, batch_size=args.batch_size, execute=args.execute).run()
    val = res["payload"]["validation"]
    master = res["payload"]["master_record"]
    quality = res["payload"]["quality"]
    decision = "PRODUCTION PILOT CERTIFICATE READY" if not val["errors"] else "PRODUCTION PILOT CERTIFICATE BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "topics": master["overall"]["topic_count"], "confidence": master["overall"]["average_confidence"], "success_probability": master["overall"]["average_success_probability"], "quality": quality["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "1960_production_pilot_certificate.json"
    state = MODULE_DIR / ("1960_production_pilot_certificate_state_" + ts + ".json")
    report = REPORTS / ("1960_production_pilot_certificate_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score             : " + str(analysis["score"]) + " / 100", "Decision          : " + str(analysis["decision"]), "Topics            : " + str(analysis["topics"]), "Confidence        : " + str(analysis["confidence"]) + " / 100", "Success Prob.     : " + str(analysis["success_probability"]) + " / 100", "Quality           : " + str(analysis["quality"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
