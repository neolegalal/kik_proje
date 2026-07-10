# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2411_2421"))
from core.neolegal_live_production_engine_sdk import NeoLegalLiveProductionEngineSDK
MODULE_DIR=BASE/"production_state"/"live_production_engine"/"2421_intelligent_batch_optimizer_auto_worker_scaler"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=int,default=10)
    p.add_argument("--batch-size",type=int,default=10)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalLiveProductionEngineSDK(target=a.target,batch_size=a.batch_size,workers=a.workers,execute=a.execute).run()
    v=r["payload"]["validation"]; s=r["payload"]["live_production_state"]
    decision="INTELLIGENT BATCH OPTIMIZER AUTO WORKER SCALER READY" if not v["errors"] else "INTELLIGENT BATCH OPTIMIZER AUTO WORKER SCALER BLOCKED"
    analysis={"score":v["score"],"decision":decision,"target":s["target"],"batch_count":s["queue"]["batch_count"],"workers":s["workers"],"recommended_workers":s["optimizer"]["recommended_workers"],"recommended_batch_size":s["optimizer"]["recommended_batch_size"],"audit":r["payload"]["audit"]["status"]}
    stamp=ts(); out=MODULE_DIR/"2421_intelligent_batch_optimizer_auto_worker_scaler.json"; rep=REPORTS/("2421_intelligent_batch_optimizer_auto_worker_scaler_raporu_"+stamp+".txt")
    out.write_text(json.dumps(analysis,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"2421 INTELLIGENT BATCH OPTIMIZER AUTO WORKER SCALER","="*80,"Score                  : "+str(analysis["score"])+" / 100","Decision               : "+decision,"Target                 : "+str(analysis["target"]),"Batch Count            : "+str(analysis["batch_count"]),"Workers                : "+str(analysis["workers"]),"Recommended Workers    : "+str(analysis["recommended_workers"]),"Recommended Batch Size : "+str(analysis["recommended_batch_size"]),"Audit                  : "+str(analysis["audit"])]
    rep.write_text("\n".join(lines),encoding="utf-8"); print("\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
