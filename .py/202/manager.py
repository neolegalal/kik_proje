# -*- coding: utf-8 -*-
import argparse
from registry import run as run_registry
from history import run as run_history
from scheduler import record_plan
from engine import run as run_engine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--engine", action="store_true")
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()

    if args.history:
        h = run_history()
        print("="*80)
        print("202 PACKAGE HISTORY TAMAMLANDI")
        print("="*80)
        print(f"Decision : {h['result']['decision']} ({h['result']['score']}/100)")
        print(h["paths"]["report"])
        return

    if args.engine:
        e = run_engine(record_history=True)
        print("="*80)
        print("202 v2 SCHEDULER ENGINE TAMAMLANDI")
        print("="*80)
        print(f"Decision     : {e['result']['decision']} ({e['result']['score']}/100)")
        print(f"Total Jobs   : {e['payload']['total_jobs']}")
        print(f"Planned Jobs : {e['payload']['planned_jobs']}")
        print("")
        print("Dosyalar:")
        print(e["paths"]["report"])
        return

    if args.plan:
        p = record_plan()
        print("="*80)
        print("202 PACKAGE SCHEDULER PLAN TAMAMLANDI")
        print("="*80)
        print(f"Decision     : {p['result']['decision']} ({p['result']['score']}/100)")
        print(f"Total Jobs   : {len(p['jobs'])}")
        print(f"Enabled Jobs : {len(p['enabled_jobs'])}")
        return

    r = run_registry(init=args.init)
    print("="*80)
    print("202 PACKAGE SCHEDULER TAMAMLANDI")
    print("="*80)
    print(f"Decision : {r['result']['decision']} ({r['result']['score']}/100)")
    print(f"Jobs     : {len(r['registry'].get('jobs', []))}")
    print("")
    print("Dosyalar:")
    print(r["paths"]["registry"])
    print(r["paths"]["report"])

if __name__ == "__main__":
    main()
