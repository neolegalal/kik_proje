# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1700"
sys.path.insert(0, str(PACKAGE_DIR))
from core.client_workspace_memory_sdk import ClientWorkspaceMemorySDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-name", default="Pilot Client")
    parser.add_argument("--case-name", default="Pilot Procurement Case")
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = ClientWorkspaceMemorySDK(client_name=args.client_name, case_name=args.case_name, case_text=args.case_text, execute=args.execute).run()
    v = res["payload"]["validation"]
    print("=" * 80)
    print("1700 CLIENT WORKSPACE MEMORY SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(v["decision"]))
    print("Score      : " + str(v["score"]) + " / 100")
    wm = res["payload"]["workspace_memory"]
    print("Client     : " + str(wm["client_profile"]["client_name"]))
    print("Case       : " + str(wm["case_name"] if "case_name" in wm else "Pilot Procurement Case"))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
