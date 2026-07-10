# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("900", "Production Master SDK", [sys.executable, str(BASE / ".py" / "900_Production_Master_SDK.py")]),
    ("901", "Production Queue Manager", [sys.executable, str(BASE / ".py" / "901_production_queue_manager.py")]),
    ("902", "Batch Manager", [sys.executable, str(BASE / ".py" / "902_batch_manager.py")]),
    ("903", "Worker Manager", [sys.executable, str(BASE / ".py" / "903_worker_manager.py")]),
    ("904", "Cost Manager", [sys.executable, str(BASE / ".py" / "904_cost_manager.py")]),
    ("905", "Progress Monitor", [sys.executable, str(BASE / ".py" / "905_progress_monitor.py")]),
    ("906", "Live Dashboard", [sys.executable, str(BASE / ".py" / "906_live_dashboard.py")]),
    ("907", "Quality Monitor", [sys.executable, str(BASE / ".py" / "907_quality_monitor.py")]),
    ("908", "Production Auditor", [sys.executable, str(BASE / ".py" / "908_production_auditor.py")]),
    ("909", "Executive Report", [sys.executable, str(BASE / ".py" / "909_executive_report.py")]),
    ("910", "Production Commander", [sys.executable, str(BASE / ".py" / "910_production_commander.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    print('='*80); print('900 PRODUCTION MASTER RUN ALL BASLADI'); print('='*80)
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
    payload={'created_at':now_text(),'program':'900 Production Master','target':args.target,'batch_size':args.batch_size,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'900_production_master_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('900 PRODUCTION MASTER SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(35)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
