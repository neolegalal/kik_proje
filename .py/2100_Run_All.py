# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"; SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS=[('2100', 'NeoLegal Legal Brain SDK', '2100_NeoLegal_Legal_Brain_SDK.py'), ('2101', 'Legal Memory', '2101_legal_memory.py'), ('2102', 'Legal Thinking Engine', '2102_legal_thinking_engine.py'), ('2103', 'Alternative Outcome Simulator', '2103_alternative_outcome_simulator.py'), ('2104', 'Judge Simulation', '2104_judge_simulation.py'), ('2105', 'Opposition Simulation', '2105_opposition_simulation.py'), ('2106', 'Hearing Simulation', '2106_hearing_simulation.py'), ('2107', 'Negotiation Engine', '2107_negotiation_engine.py'), ('2108', 'Legal Copilot Core', '2108_legal_copilot_core.py'), ('2109', 'Self Reflection Engine', '2109_self_reflection_engine.py'), ('2110', 'Legal Brain Certificate', '2110_legal_brain_certificate.py')]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--case-text",default=None); p.add_argument("--master-record",default=None); p.add_argument("--execute",action="store_true"); a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2100 NEOLEGAL LEGAL BRAIN RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file)]
        if a.case_text: cmd+=["--case-text",a.case_text]
        if a.master_record: cmd+=["--master-record",a.master_record]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE)); status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"; rows.append({"module_id":mid,"name":name,"status":status})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2100 NeoLegal Legal Brain","modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}
    path=SUMMARY/"2100_neolegal_legal_brain_summary.json"; path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"="*80); print("2100 NEOLEGAL LEGAL BRAIN SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(42)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\nSummary JSON:\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
