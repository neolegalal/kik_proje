# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("801", "Production Safety Gate SDK", [sys.executable, str(BASE / ".py" / "801_Production_Safety_Gate_SDK.py")]),
    ("811", "Database Safety Checker", [sys.executable, str(BASE / ".py" / "811_database_safety_checker.py")]),
    ("812", "Pipeline Safety Checker", [sys.executable, str(BASE / ".py" / "812_pipeline_safety_checker.py")]),
    ("813", "API Cost Safety Checker", [sys.executable, str(BASE / ".py" / "813_api_cost_safety_checker.py")]),
    ("814", "Output Isolation Checker", [sys.executable, str(BASE / ".py" / "814_output_isolation_checker.py")]),
    ("815", "Duplicate Risk Checker", [sys.executable, str(BASE / ".py" / "815_duplicate_risk_checker.py")]),
    ("816", "Backup Rollback Checker", [sys.executable, str(BASE / ".py" / "816_backup_rollback_checker.py")]),
    ("817", "Resume Recovery Checker", [sys.executable, str(BASE / ".py" / "817_resume_recovery_checker.py")]),
    ("818", "Resource Capacity Checker", [sys.executable, str(BASE / ".py" / "818_resource_capacity_checker.py")]),
    ("819", "Git State Checker", [sys.executable, str(BASE / ".py" / "819_git_state_checker.py")]),
    ("820", "Production Launch Gate", [sys.executable, str(BASE / ".py" / "820_production_launch_gate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); args=parser.parse_args()
    print('='*80); print('801 PRODUCTION SAFETY GATE RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id,name,cmd in COMMANDS:
        full_cmd=cmd+['--batch-size', str(args.batch_size)]
        print('\n>>> '+' '.join(full_cmd)); result=subprocess.run(full_cmd, cwd=str(BASE))
        status='PASS' if result.returncode==0 else 'FAIL'
        if status=='PASS': passed+=1
        else: failed+=1
        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'801 Production Safety Gate','batch_size':args.batch_size,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'801_production_safety_gate_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('801 PRODUCTION SAFETY GATE SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
