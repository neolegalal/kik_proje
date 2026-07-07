# -*- coding: utf-8 -*-
import argparse
from core.sdk import SchedulerSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    res = SchedulerSDK().run()
    payload = res["payload"]
    validation = payload["validation"]
    decision = payload["decision"]
    print("="*80)
    print("206.0 SCHEDULER SDK TAMAMLANDI")
    print("="*80)
    print("Validation : " + str(validation["decision"]))
    print("Score      : " + str(validation["score"]) + " / 100")
    print("Errors     : " + str(len(validation["errors"])))
    print("Warnings   : " + str(len(validation["warnings"])))
    print("Decision   : " + str(decision["decision"]))
    print("Risk       : " + str(decision["risk"]))
    print("Batch Size : " + str(decision["recommended_batch_size"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
