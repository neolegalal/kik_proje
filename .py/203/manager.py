# -*- coding: utf-8 -*-
import argparse
from logger import run_test
from auditor import run as run_audit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--test-log", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--tail", type=int, default=50)
    parser.add_argument("--problems", action="store_true")
    args = parser.parse_args()

    if args.test_log:
        res = run_test()
        print("="*80)
        print("203 CENTRAL LOGGER TEST TAMAMLANDI")
        print("="*80)
        print(f"Decision : {res['result']['decision']} ({res['result']['score']}/100)")
        print("")
        print("Dosyalar:")
        print(res["paths"]["log"])
        print(res["paths"]["report"])
        return

    res = run_audit(limit=args.tail, problems=args.problems)
    print("="*80)
    print("203 CENTRAL LOGGER AUDIT TAMAMLANDI")
    print("="*80)
    print(f"Decision     : {res['result']['decision']} ({res['result']['score']}/100)")
    print(f"Total Logs   : {res['summary']['total']}")
    print(f"Problem Logs : {len(res['summary']['problem_logs'])}")
    print(f"Invalid      : {res['summary']['invalid']}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["log"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
