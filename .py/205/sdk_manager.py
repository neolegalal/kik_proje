# -*- coding: utf-8 -*-
import argparse
from core.engine import IntelligenceEngine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = IntelligenceEngine(engine_name="SDK Self Test")
    res = engine.run()
    result = res["payload"]["result"]

    print("="*80)
    print("205.0 INTELLIGENCE SDK TAMAMLANDI")
    print("="*80)
    print(f"Score          : {result['score']} / 100")
    print(f"Decision       : {result['decision']}")
    print(f"Risk Level     : {result['risk_level']}")
    print(f"Risk Reasons   : {len(result['risk_reasons'])}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["output"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
