# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1100"
sys.path.insert(0, str(PACKAGE_DIR))
from core.decision_processing_pipeline_sdk import DecisionProcessingPipelineSDK
STATE = BASE / "production_state"; REPORTS = BASE / "raporlar"; MODULE_DIR = STATE / "decision_processing_pipeline" / "1109_web_rag_card_builder"
MODULE_ID = "1109"; MODULE_NAME = "Web Rag Card Builder"
def now_stamp(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    res = DecisionProcessingPipelineSDK(name=MODULE_ID + " " + MODULE_NAME, batch_size=args.batch_size, execute=args.execute).run(); val = res["payload"]["validation"]
    decision = "WEB RAG CARD BUILDER READY" if not val["errors"] else "WEB RAG CARD BUILDER BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "cards": val["total"], "pass_count": val["pass_count"], "average_quality": val["average_card_quality"], "recommendation": "Decision processing module ready." if not val["errors"] else "Decision processing module blocked."}
    ts = now_stamp(); output = MODULE_DIR / "1109_web_rag_card_builder.json"; state = MODULE_DIR / ("1109_web_rag_card_builder_state_" + ts + ".json"); report = REPORTS / ("1109_web_rag_card_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload); write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score    : " + str(analysis["score"]) + " / 100", "Decision : " + str(analysis["decision"]), "Cards    : " + str(analysis["cards"]), "PASS     : " + str(analysis["pass_count"]), "AvgQual  : " + str(analysis["average_quality"]), "", "Recommendation:", str(analysis["recommendation"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8"); print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__": main()
