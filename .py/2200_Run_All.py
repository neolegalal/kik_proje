# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"
SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS=[('2200', 'NeoLegal Autonomous Legal Expert SDK', '2200_NeoLegal_Autonomous_Legal_Expert_SDK.py'), ('2201', 'Autonomous Case Intake', '2201_autonomous_case_intake.py'), ('2202', 'Automatic Evidence Analyzer', '2202_automatic_evidence_analyzer.py'), ('2203', 'Legal Strategy Planner', '2203_legal_strategy_planner.py'), ('2204', 'Defense Generator', '2204_defense_generator.py'), ('2205', 'Complaint Generator', '2205_complaint_generator.py'), ('2206', 'Appeal Generator', '2206_appeal_generator.py'), ('2207', 'Case Success Predictor', '2207_case_success_predictor.py'), ('2208', 'Client Workspace AI', '2208_client_workspace_ai.py'), ('2209', 'Continuous Self Learning', '2209_continuous_self_learning.py'), ('2210', 'Autonomous Expert Certificate', '2210_autonomous_expert_certificate.py')]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file),"--client-name",a.client_name,"--case-name",a.case_name]
        if a.case_text: cmd+=["--case-text",a.case_text]
        if a.master_record: cmd+=["--master-record",a.master_record]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE))
        status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"
        rows.append({"module_id":mid,"name":name,"status":status,"returncode":r.returncode})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2200 NeoLegal Autonomous Legal Expert","modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}
    path=SUMMARY/"2200_neolegal_autonomous_legal_expert_summary.json"
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"="*80); print("2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(42)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\nSummary JSON:\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
