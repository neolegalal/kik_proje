
# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1300"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_advisory_intelligence_sdk import LegalAdvisoryIntelligenceSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--advisory-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = LegalAdvisoryIntelligenceSDK(case_text=args.case_text, advisory_type=args.advisory_type, execute=args.execute).run()
    v = res["payload"]["validation"]
    advisory = res["payload"]["advisory"]
    print("=" * 80)
    print("1300 LEGAL ADVISORY INTELLIGENCE SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Success Probability : " + str(advisory["outcome_probability"]["success_probability"]) + " / 100")
    print("Court Risk          : " + str(advisory["court_risk"]["court_risk"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
