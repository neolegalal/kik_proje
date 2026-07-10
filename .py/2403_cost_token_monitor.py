# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2400"))
from core.neolegal_production_execution_center_sdk import NeoLegalProductionExecutionCenterSDK
MODULE_DIR=BASE/"production_state"/"production_execution_center"/"2403_cost_token_monitor"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=int,default=100000)
    p.add_argument("--batch-size",type=int,default=100)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--mode",default="dry-run")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalProductionExecutionCenterSDK(name="2403 Cost Token Monitor",target=a.target,batch_size=a.batch_size,workers=a.workers,mode=a.mode,execute=a.execute).run()
    v=r["payload"]["validation"]; e=r["payload"]["execution_state"]
    decision="COST TOKEN MONITOR READY" if not v["errors"] else "COST TOKEN MONITOR BLOCKED"
    analysis={"score":v["score"],"decision":decision,"target":e["target"],"batch_count":e["queue"]["batch_count"],"workers":e["workers"],"estimated_cost_usd":e["cost"]["estimated_cost_usd"],"quality_gate":e["quality"]["decision"],"audit":e["audit"]["status"]}
    stamp=ts(); out=MODULE_DIR/"2403_cost_token_monitor.json"; state=MODULE_DIR/("2403_cost_token_monitor_state_"+stamp+".json"); rep=REPORTS/("2403_cost_token_monitor_raporu_"+stamp+".txt")
    payload={"module_id":"2403","module_name":"Cost Token Monitor","analysis":analysis,"sdk_reference":r["paths"]}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); state.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"2403 COST TOKEN MONITOR","="*80,"Score              : "+str(analysis["score"])+" / 100","Decision           : "+decision,"Target             : "+str(analysis["target"]),"Batch Count        : "+str(analysis["batch_count"]),"Workers            : "+str(analysis["workers"]),"Estimated Cost USD : "+str(analysis["estimated_cost_usd"]),"Quality Gate       : "+str(analysis["quality_gate"]),"Audit              : "+str(analysis["audit"])]
    rep.write_text("\n".join(lines),encoding="utf-8"); print("\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
