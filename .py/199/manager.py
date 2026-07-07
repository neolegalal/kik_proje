# -*- coding: utf-8 -*-
import argparse
from registry import run as run_registry
from health import run as run_health

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", action="store_true")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.all or (not args.registry and not args.health):
        reg = run_registry()
        health = run_health()
        print("="*80)
        print("199 PACKAGE MANAGER TAMAMLANDI")
        print("="*80)
        print(f"Registry : {reg['result']['decision']} ({reg['result']['score']}/100)")
        print(f"Health   : {health['result']['decision']} ({health['result']['score']}/100)")
        print("")
        print("Dosyalar:")
        print(reg["paths"]["report"])
        print(health["paths"]["report"])
        return
    if args.registry:
        reg = run_registry()
        print(f"Registry : {reg['result']['decision']} ({reg['result']['score']}/100)")
    if args.health:
        health = run_health()
        print(f"Health : {health['result']['decision']} ({health['result']['score']}/100)")

if __name__ == "__main__":
    main()
