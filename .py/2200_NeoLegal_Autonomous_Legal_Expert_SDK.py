# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2200"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_autonomous_legal_expert_sdk import NeoLegalAutonomousLegalExpertSDK

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalAutonomousLegalExpertSDK(case_text=a.case_text,client_name=a.client_name,case_name=a.case_name,master_record_path=a.master_record,execute=a.execute).run()
    v=r["payload"]["validation"]; e=r["payload"]["expert_state"]
    print("="*80)
    print("2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT SDK TAMAMLANDI")
    print("="*80)
    print("Validation          : "+str(v["decision"]))
    print("Score               : "+str(v["score"])+" / 100")
    print("Issue Count         : "+str(e["intake"]["issue_count"]))
    print("Evidence Risk       : "+str(e["evidence"]["risk"]))
    print("Success Probability : "+str(e["prediction"]["success_probability"])+" / 100")
    print("Workspace           : "+str(e["workspace"]["root"]))
    print("")
    print("Dosyalar:")
    print(r["paths"]["snapshot"])
    print(r["paths"]["expert_state"])
    print(r["paths"]["dashboard"])
    print(r["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__=="__main__":
    main()
