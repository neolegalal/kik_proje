# -*- coding: utf-8 -*-
import argparse
from core import run as run_core
from config_manager import run as run_config
from lifecycle import run as run_lifecycle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--registry", action="store_true")
    parser.add_argument("--config", action="store_true")
    parser.add_argument("--lifecycle", choices=["startup", "shutdown", "maintenance", "status"])
    parser.add_argument("--plan", action="store_true")
    args = parser.parse_args()

    if args.config:
        res = run_config()
        print("="*80); print("200 PACKAGE CONFIG TAMAMLANDI"); print("="*80)
        print(f"Decision : {res['result']['decision']} ({res['result']['score']}/100)")
        print(res["paths"]["report"])
        return

    if args.lifecycle:
        res = run_lifecycle(args.lifecycle)
        print("="*80); print("200 PACKAGE LIFECYCLE TAMAMLANDI"); print("="*80)
        print(f"Decision : {res['result']['decision']} ({res['result']['score']}/100)")
        print(res["paths"]["report"])
        return

    mode = "status"
    if args.health:
        mode = "health"
    elif args.registry:
        mode = "registry"
    elif args.plan:
        mode = "plan"

    res = run_core(mode=mode)
    print("="*80)
    print("200 PACKAGE MANAGER TAMAMLANDI")
    print("="*80)
    print(f"Mode     : {mode}")
    print(f"Decision : {res['result']['decision']} ({res['result']['score']}/100)")
    print(f"Errors   : {len(res['result']['errors'])}")
    print(f"Warnings : {len(res['result']['warnings'])}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
