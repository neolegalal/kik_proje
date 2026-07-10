# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1950"
sys.path.insert(0, str(PACKAGE_DIR))
from core.unified_decision_processor_sdk import UnifiedDecisionProcessorSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-text", default=None)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = UnifiedDecisionProcessorSDK(decision_text=args.decision_text, batch_size=args.batch_size, execute=args.execute).run()
    v = res["payload"]["validation"]
    master = res["payload"]["master_record"]
    quality = res["payload"]["quality"]
    print("=" * 80)
    print("1950 UNIFIED DECISION PROCESSOR SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation              : " + str(v["decision"]))
    print("Score                   : " + str(v["score"]) + " / 100")
    print("Dispute Topics          : " + str(master["overall"]["topic_count"]))
    print("Average Confidence      : " + str(master["overall"]["average_confidence"]) + " / 100")
    print("Average Success Prob.   : " + str(master["overall"]["average_success_probability"]) + " / 100")
    print("Quality                 : " + str(quality["status"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["master"])
    print(res["paths"]["web"])
    print(res["paths"]["rag"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
