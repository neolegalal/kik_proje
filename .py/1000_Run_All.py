# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1000", "Production Operations SDK", [sys.executable, str(BASE / ".py" / "1000_Production_Operations_SDK.py")]),
    ("1001", "Production Scheduler", [sys.executable, str(BASE / ".py" / "1001_production_scheduler.py")]),
    ("1002", "Smart Queue Optimizer", [sys.executable, str(BASE / ".py" / "1002_smart_queue_optimizer.py")]),
    ("1003", "Batch Execution Manager", [sys.executable, str(BASE / ".py" / "1003_batch_execution_manager.py")]),
    ("1004", "Cost Tracking Center", [sys.executable, str(BASE / ".py" / "1004_cost_tracking_center.py")]),
    ("1005", "Token Analytics", [sys.executable, str(BASE / ".py" / "1005_token_analytics.py")]),
    ("1006", "Quality Analytics", [sys.executable, str(BASE / ".py" / "1006_quality_analytics.py")]),
    ("1007", "Human Review Center", [sys.executable, str(BASE / ".py" / "1007_human_review_center.py")]),
    ("1008", "Live Production Dashboard", [sys.executable, str(BASE / ".py" / "1008_live_production_dashboard.py")]),
    ("1009", "Production KPI Center", [sys.executable, str(BASE / ".py" / "1009_production_kpi_center.py")]),
    ("1010", "Executive Control Center", [sys.executable, str(BASE / ".py" / "1010_executive_control_center.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    print('='*80); print('1000 PRODUCTION OPERATIONS RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id,name,cmd in COMMANDS:
        full=cmd+['--target',str(args.target),'--batch-size',str(args.batch_size)]
        if args.execute: full.append('--execute')
        print('\n>>> '+' '.join(full)); result=subprocess.run(full, cwd=str(BASE))
        status='PASS' if result.returncode==0 else 'FAIL'
        if status=='PASS': passed+=1
        else: failed+=1
        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1000 Production Operations','target':args.target,'batch_size':args.batch_size,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1000_production_operations_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('1000 PRODUCTION OPERATIONS SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(35)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
