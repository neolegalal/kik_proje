# -*- coding: utf-8 -*-
import argparse
from engines.db_growth_analytics import DbGrowthAnalyticsEngine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = DbGrowthAnalyticsEngine()
    res = engine.run()
    result = res["result"]
    growth = res["payload"]["growth"]

    print("=" * 80)
    print("205.4 DB GROWTH ANALYTICS TAMAMLANDI")
    print("=" * 80)
    print(f"Score          : {result['score']} / 100")
    print(f"Decision       : {result['decision']}")
    print(f"Risk           : {result['risk']}")
    print(f"DB Count       : {growth['current_db_count']}")
    print(f"Remaining      : {growth['remaining_to_target']}")
    print(f"Progress       : {growth['progress_percent']}%")
    print(f"Forecast       : {growth['estimated_cycles_to_target']}")
    print(f"Confidence     : {growth['forecast_confidence']}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["growth"])
    print(res["paths"]["report"])


if __name__ == "__main__":
    main()
