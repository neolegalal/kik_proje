# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2300"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_platform_governance_sdk import NeoLegalPlatformGovernanceSDK

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalPlatformGovernanceSDK(environment=a.environment,execute=a.execute).run()
    v=r["payload"]["validation"]; g=r["payload"]["governance_state"]
    print("="*80)
    print("2300 NEOLEGAL PLATFORM GOVERNANCE SDK TAMAMLANDI")
    print("="*80)
    print("Validation       : "+str(v["decision"]))
    print("Score            : "+str(v["score"])+" / 100")
    print("Security Score   : "+str(g["security"]["policy_score"])+" / 100")
    print("Compliance Score : "+str(g["compliance"]["compliance_score"])+" / 100")
    print("Environment      : "+str(g["certificate"]["environment"]))
    print("")
    print("Dosyalar:")
    print(r["paths"]["snapshot"])
    print(r["paths"]["governance_state"])
    print(r["paths"]["dashboard"])
    print(r["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__=="__main__":
    main()
