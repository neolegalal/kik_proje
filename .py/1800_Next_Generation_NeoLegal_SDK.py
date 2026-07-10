# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1800"
sys.path.insert(0, str(PACKAGE_DIR))
from core.next_generation_neolegal_sdk import NextGenerationNeoLegalSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = NextGenerationNeoLegalSDK(case_text=args.case_text, mode=args.mode, execute=args.execute).run()
    v = res["payload"]["validation"]
    ng = res["payload"]["next_generation"]
    print("=" * 80)
    print("1800 NEXT GENERATION NEOLEGAL AI SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(v["decision"]))
    print("Score      : " + str(v["score"]) + " / 100")
    print("Prediction : " + str(ng["prediction_engine"]["base_success_probability"]) + " / 100")
    print("Audit      : " + str(ng["audit"]["status"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
