# -*- coding: utf-8 -*-
import argparse
from core.sdk import AutomationSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    res = AutomationSDK().run()
    payload = res["payload"]
    validation = payload["validation"]
    plan = payload["plan"]

    print("=" * 80)
    print("208.0 AUTOMATION SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(validation["decision"]))
    print("Score      : " + str(validation["score"]) + " / 100")
    print("Errors     : " + str(len(validation["errors"])))
    print("Warnings   : " + str(len(validation["warnings"])))
    print("Mode       : " + str(plan["automation_mode"]))
    print("Triggers   : " + str(len(plan["triggers"])))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
