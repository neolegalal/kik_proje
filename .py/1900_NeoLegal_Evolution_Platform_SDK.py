# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1900"
sys.path.insert(0, str(PACKAGE_DIR))
from core.neolegal_evolution_platform_sdk import NeoLegalEvolutionPlatformSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = NeoLegalEvolutionPlatformSDK(sample_text=args.sample_text, mode=args.mode, execute=args.execute).run()
    v = res["payload"]["validation"]
    evo = res["payload"]["evolution"]
    print("=" * 80)
    print("1900 NEOLEGAL EVOLUTION PLATFORM SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Knowledge Confidence: " + str(evo["confidence"]["confidence_score"]) + " / 100")
    print("Hallucination Risk  : " + str(evo["hallucination"]["hallucination_risk"]) + " / 100")
    print("Evidence Count      : " + str(evo["evidence"]["evidence_count"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
