# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1600"
sys.path.insert(0, str(PACKAGE_DIR))
from core.neolegal_expert_orchestrator_sdk import NeoLegalExpertOrchestratorSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--expert-mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = NeoLegalExpertOrchestratorSDK(case_text=args.case_text, expert_mode=args.expert_mode, execute=args.execute).run()
    v = res["payload"]["validation"]
    print("=" * 80)
    print("1600 NEOLEGAL EXPERT ORCHESTRATOR SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(v["decision"]))
    print("Score      : " + str(v["score"]) + " / 100")
    expert = res["payload"]["expert"]
    print("Success Probability : " + str(expert["advisory"]["success_probability"]) + " / 100")
    print("Risk                : " + str(expert["advisory"]["risk_level"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
