# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1400"
sys.path.insert(0, str(PACKAGE_DIR))
from core.litigation_intelligence_platform_sdk import LitigationIntelligencePlatformSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--litigation-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = LitigationIntelligencePlatformSDK(case_text=args.case_text, litigation_type=args.litigation_type, execute=args.execute).run()
    v = res["payload"]["validation"]
    lit = res["payload"]["litigation"]
    print("=" * 80)
    print("1400 LITIGATION INTELLIGENCE PLATFORM SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Success Probability : " + str(lit["probability"]["success_probability"]) + " / 100")
    print("YD Score            : " + str(lit["stay_of_execution"]["score"]) + " / 100")
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
