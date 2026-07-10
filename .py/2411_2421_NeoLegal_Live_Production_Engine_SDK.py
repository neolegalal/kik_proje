# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2411_2421"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_live_production_engine_sdk import NeoLegalLiveProductionEngineSDK

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=int,default=10)
    p.add_argument("--batch-size",type=int,default=10)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalLiveProductionEngineSDK(target=a.target,batch_size=a.batch_size,workers=a.workers,execute=a.execute).run()
    v=r["payload"]["validation"]; s=r["payload"]["live_production_state"]
    print("="*80)
    print("2411-2421 NEOLEGAL LIVE PRODUCTION ENGINE SDK TAMAMLANDI")
    print("="*80)
    print("Validation             : "+str(v["decision"]))
    print("Score                  : "+str(v["score"])+" / 100")
    print("Target                 : "+str(s["target"]))
    print("Batch Count            : "+str(s["queue"]["batch_count"]))
    print("Workers                : "+str(s["workers"]))
    print("Recommended Workers    : "+str(s["optimizer"]["recommended_workers"]))
    print("Recommended Batch Size : "+str(s["optimizer"]["recommended_batch_size"]))
    print("Supervisor Decision    : "+str(s["supervisor"]["decision"]))
    print("")
    print("Dosyalar:")
    print(r["paths"]["snapshot"])
    print(r["paths"]["runtime"])
    print(r["paths"]["dashboard"])
    print(r["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__=="__main__":
    main()
