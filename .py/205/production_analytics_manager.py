# -*- coding: utf-8 -*-
import argparse
from engines.production_analytics import ProductionAnalyticsEngine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = ProductionAnalyticsEngine()
    res = engine.run()
    result = res["result"]
    payload = res["payload"]

    print("="*80)
    print("205.1 PRODUCTION ANALYTICS ENGINE TAMAMLANDI")
    print("="*80)
    print(f"Score        : {result['score']} / 100")
    print(f"Decision     : {result['decision']}")
    print(f"Risk         : {result['risk']}")
    print(f"DB Count     : {payload['growth']['current_db_count']}")
    print(f"Remaining    : {payload['growth']['remaining_to_target']}")
    print(f"Capacity     : {payload['capacity']['capacity_level']}")
    print(f"Forecast     : {payload['forecast']['estimated_cycles_to_target']}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["analytics"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
