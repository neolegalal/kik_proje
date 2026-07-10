# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "2050"
sys.path.insert(0, str(PACKAGE_DIR))
from core.validation_benchmark_platform_sdk import ValidationBenchmarkPlatformSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold-standard", default=None)
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = ValidationBenchmarkPlatformSDK(gold_standard_path=args.gold_standard, master_record_path=args.master_record, execute=args.execute).run()
    v = res["payload"]["validation"]
    acc = res["payload"]["accuracy"]
    hall = res["payload"]["hallucination"]
    cons = res["payload"]["consistency"]
    cont = res["payload"]["continuous_benchmark"]
    print("=" * 80)
    print("2050 VALIDATION & BENCHMARK PLATFORM SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation           : " + str(v["decision"]))
    print("Score                : " + str(v["score"]) + " / 100")
    print("Accuracy             : " + str(acc["accuracy"]) + " / 100")
    print("Main Issue Detection : " + str(acc["main_issue_detection"]) + " / 100")
    print("Citation Accuracy    : " + str(acc["citation_accuracy"]) + " / 100")
    print("Hallucination Rate   : " + str(hall["hallucination_rate"]) + " / 100")
    print("Consistency          : " + str(cons["consistency_score"]) + " / 100")
    print("Release Gate         : " + str(cont["release_gate"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["gold"])
    print(res["paths"]["benchmark"])
    print(res["paths"]["scientific"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
