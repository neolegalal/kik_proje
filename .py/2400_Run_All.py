# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"
SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS=[('2400', 'NeoLegal Production Execution Center SDK', '2400_NeoLegal_Production_Execution_Center_SDK.py'), ('2401', 'Production Queue Manager', '2401_production_queue_manager.py'), ('2402', 'Parallel Worker Orchestrator', '2402_parallel_worker_orchestrator.py'), ('2403', 'Cost Token Monitor', '2403_cost_token_monitor.py'), ('2404', 'Quality Gate Controller', '2404_quality_gate_controller.py'), ('2405', 'Retry Recovery Manager', '2405_retry_recovery_manager.py'), ('2406', 'Checkpoint Resume Engine', '2406_checkpoint_resume_engine.py'), ('2407', 'Publication Export Manager', '2407_publication_export_manager.py'), ('2408', 'Live Production Dashboard', '2408_live_production_dashboard.py'), ('2409', 'Production Audit Center', '2409_production_audit_center.py'), ('2410', 'Production Execution Certificate', '2410_production_execution_certificate.py')]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--target",type=int,default=100000)
    p.add_argument("--batch-size",type=int,default=100)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--mode",default="dry-run")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2400 NEOLEGAL PRODUCTION EXECUTION CENTER RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file),"--target",str(a.target),"--batch-size",str(a.batch_size),"--workers",str(a.workers),"--mode",a.mode]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE))
        status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"
        rows.append({"module_id":mid,"name":name,"status":status,"returncode":r.returncode})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2400 NeoLegal Production Execution Center","target":a.target,"batch_size":a.batch_size,"workers":a.workers,"mode":a.mode,"modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}
    path=SUMMARY/"2400_neolegal_production_execution_center_summary.json"
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"="*80); print("2400 NEOLEGAL PRODUCTION EXECUTION CENTER SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(42)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\nSummary JSON:\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
