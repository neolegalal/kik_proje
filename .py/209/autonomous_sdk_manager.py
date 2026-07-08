# -*- coding: utf-8 -*-
import argparse
from core.sdk import AutonomousSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    res = AutonomousSDK().run()
    payload = res["payload"]
    validation = payload["validation"]
    plan = payload["plan"]

    print("=" * 80)
    print("209.0 AUTONOMOUS OPERATIONS SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(validation["decision"]))
    print("Score      : " + str(validation["score"]) + " / 100")
    print("Errors     : " + str(len(validation["errors"])))
    print("Warnings   : " + str(len(validation["warnings"])))
    print("Mode       : " + str(plan["operation_mode"]))
    print("Operations : " + str(len(plan["operations"])))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
