# -*- coding: utf-8 -*-
import argparse
from engines.queue_intelligence import QueueIntelligenceEngine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = QueueIntelligenceEngine()
    res = engine.run()
    result = res["result"]
    payload = res["payload"]

    print("="*80)
    print("205.2 QUEUE INTELLIGENCE ENGINE TAMAMLANDI")
    print("="*80)
    print(f"Score          : {result['score']} / 100")
    print(f"Decision       : {result['decision']}")
    print(f"Risk           : {result['risk']}")
    print(f"Total Jobs     : {payload['backlog']['total']}")
    print(f"Waiting        : {payload['backlog']['waiting']}")
    print(f"Finished       : {payload['backlog']['finished']}")
    print(f"Failed         : {payload['backlog']['failed']}")
    print(f"Completion     : {payload['completion']['completion_rate']}%")
    print(f"Worker Fit     : {payload['worker_fit']['worker_queue_fit']}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["queue"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
