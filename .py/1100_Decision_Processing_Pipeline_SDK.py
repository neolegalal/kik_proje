# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1100"
sys.path.insert(0, str(PACKAGE_DIR))
from core.decision_processing_pipeline_sdk import DecisionProcessingPipelineSDK

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    res = DecisionProcessingPipelineSDK(batch_size=args.batch_size, execute=args.execute).run(); v = res["payload"]["validation"]
    print("=" * 80); print("1100 DECISION PROCESSING PIPELINE SDK TAMAMLANDI"); print("=" * 80)
    print("Validation : " + str(v["decision"])); print("Score      : " + str(v["score"]) + " / 100"); print("Cards      : " + str(v["total"])); print("PASS       : " + str(v["pass_count"])); print("AvgQuality : " + str(v["average_card_quality"]))
    print(""); print("Dosyalar:"); print(res["paths"]["snapshot"]); print(res["paths"]["cards"]); print(res["paths"]["dashboard"]); print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)
if __name__ == "__main__": main()
