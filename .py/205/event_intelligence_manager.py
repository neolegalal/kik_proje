# -*- coding: utf-8 -*-
import argparse
from engines.event_intelligence import EventIntelligenceEngine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = EventIntelligenceEngine()
    res = engine.run()
    result = res["result"]
    analysis = res["payload"]["analysis"]

    print("=" * 80)
    print("205.5 EVENT INTELLIGENCE TAMAMLANDI")
    print("=" * 80)
    print(f"Score          : {result['score']} / 100")
    print(f"Decision       : {result['decision']}")
    print(f"Risk           : {result['risk']}")
    print(f"Event Total    : {analysis['total']}")
    print(f"Warning        : {analysis['warning']}")
    print(f"Error          : {analysis['error']}")
    print(f"Critical       : {analysis['critical']}")
    print(f"Invalid        : {analysis['invalid']}")
    print(f"Density        : {analysis['event_density']}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["event"])
    print(res["paths"]["report"])


if __name__ == "__main__":
    main()
