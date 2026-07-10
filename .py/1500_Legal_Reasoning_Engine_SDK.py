# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1500"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_reasoning_engine_sdk import LegalReasoningEngineSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--reasoning-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = LegalReasoningEngineSDK(case_text=args.case_text, reasoning_type=args.reasoning_type, execute=args.execute).run()
    v = res["payload"]["validation"]
    reasoning = res["payload"]["reasoning"]
    print("=" * 80)
    print("1500 LEGAL REASONING ENGINE SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Success Probability : " + str(reasoning["outcome_prediction"]["success_probability"]) + " / 100")
    print("Confidence          : " + str(reasoning["outcome_prediction"]["confidence"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
