# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2400"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_production_execution_center_sdk import NeoLegalProductionExecutionCenterSDK

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=int,default=100000)
    p.add_argument("--batch-size",type=int,default=100)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--mode",default="dry-run")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalProductionExecutionCenterSDK(target=a.target,batch_size=a.batch_size,workers=a.workers,mode=a.mode,execute=a.execute).run()
    v=r["payload"]["validation"]; e=r["payload"]["execution_state"]
    print("="*80)
    print("2400 NEOLEGAL PRODUCTION EXECUTION CENTER SDK TAMAMLANDI")
    print("="*80)
    print("Validation         : "+str(v["decision"]))
    print("Score              : "+str(v["score"])+" / 100")
    print("Target             : "+str(e["target"]))
    print("Batch Count        : "+str(e["queue"]["batch_count"]))
    print("Workers            : "+str(e["workers"]))
    print("Estimated Cost USD : "+str(e["cost"]["estimated_cost_usd"]))
    print("Quality Gate       : "+str(e["quality"]["decision"]))
    print("")
    print("Dosyalar:")
    print(r["paths"]["snapshot"])
    print(r["paths"]["execution_state"])
    print(r["paths"]["dashboard"])
    print(r["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__=="__main__":
    main()
