# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"
SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS=[('2300', 'NeoLegal Platform Governance SDK', '2300_NeoLegal_Platform_Governance_SDK.py'), ('2301', 'Version Manager', '2301_version_manager.py'), ('2302', 'Model Registry', '2302_model_registry.py'), ('2303', 'Data Lifecycle Manager', '2303_data_lifecycle_manager.py'), ('2304', 'Audit Log Center', '2304_audit_log_center.py'), ('2305', 'Security Policy Engine', '2305_security_policy_engine.py'), ('2306', 'Role Permission Manager', '2306_role_permission_manager.py'), ('2307', 'Monitoring KPI Center', '2307_monitoring_kpi_center.py'), ('2308', 'Compliance Manager', '2308_compliance_manager.py'), ('2309', 'Disaster Recovery Manager', '2309_disaster_recovery_manager.py'), ('2310', 'Governance Certificate', '2310_governance_certificate.py')]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2300 NEOLEGAL PLATFORM GOVERNANCE RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file),"--environment",a.environment]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE))
        status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"
        rows.append({"module_id":mid,"name":name,"status":status,"returncode":r.returncode})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2300 NeoLegal Platform Governance","environment":a.environment,"modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}
    path=SUMMARY/"2300_neolegal_platform_governance_summary.json"
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n"+"="*80); print("2300 NEOLEGAL PLATFORM GOVERNANCE SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(42)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\nSummary JSON:\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
