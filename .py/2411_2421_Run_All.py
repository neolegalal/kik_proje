# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"
SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS=[('2411-2421', 'NeoLegal Live Production Engine SDK', '2411_2421_NeoLegal_Live_Production_Engine_SDK.py'), ('2411', 'Production Execute Engine', '2411_production_execute_engine.py'), ('2412', 'Production Queue Runner', '2412_production_queue_runner.py'), ('2413', 'Production Health Monitor', '2413_production_health_monitor.py'), ('2414', 'Production Auto Recovery', '2414_production_auto_recovery.py'), ('2415', 'Production Auto Publisher', '2415_production_auto_publisher.py'), ('2416', 'Production Statistics', '2416_production_statistics.py'), ('2417', 'Production Cost Optimizer', '2417_production_cost_optimizer.py'), ('2418', 'Production Scaling Engine', '2418_production_scaling_engine.py'), ('2419', 'Production Supervisor AI', '2419_production_supervisor_ai.py'), ('2420', 'Live Production Certificate', '2420_live_production_certificate.py'), ('2421', 'Intelligent Batch Optimizer Auto Worker Scaler', '2421_intelligent_batch_optimizer_auto_worker_scaler.py')]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=int,default=10)
    p.add_argument("--batch-size",type=int,default=10)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2411-2421 NEOLEGAL LIVE PRODUCTION ENGINE RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file),"--target",str(a.target),"--batch-size",str(a.batch_size),"--workers",str(a.workers)]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE))
        status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"
        rows.append({"module_id":mid,"name":name,"status":status,"returncode":r.returncode})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2411-2421 NeoLegal Live Production Engine","target":a.target,"batch_size":a.batch_size,"workers":a.workers,"modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}
    path=SUMMARY/"2411_2421_neolegal_live_production_engine_summary.json"
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"="*80); print("2411-2421 NEOLEGAL LIVE PRODUCTION ENGINE SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(50)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\nSummary JSON:\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
