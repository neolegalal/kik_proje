# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("700", "Pilot Production Launcher SDK", [sys.executable, str(BASE / ".py" / "700_Pilot_Production_Launcher_SDK.py")]),
    ("701", "Pilot Batch Selector", [sys.executable, str(BASE / ".py" / "701_pilot_batch_selector.py")]),
    ("702", "Production Queue Launcher", [sys.executable, str(BASE / ".py" / "702_production_queue_launcher.py")]),
    ("703", "Runtime Production Executor", [sys.executable, str(BASE / ".py" / "703_runtime_production_executor.py")]),
    ("704", "Live Quality Monitor", [sys.executable, str(BASE / ".py" / "704_live_quality_monitor.py")]),
    ("705", "Production Cost Tracker", [sys.executable, str(BASE / ".py" / "705_production_cost_tracker.py")]),
    ("706", "Production Metrics Collector", [sys.executable, str(BASE / ".py" / "706_production_metrics_collector.py")]),
    ("707", "Pilot Report Generator", [sys.executable, str(BASE / ".py" / "707_pilot_report_generator.py")]),
    ("708", "Pilot Dashboard", [sys.executable, str(BASE / ".py" / "708_pilot_dashboard.py")]),
    ("709", "Pilot Auditor", [sys.executable, str(BASE / ".py" / "709_pilot_auditor.py")]),
    ("710", "Launch Certification", [sys.executable, str(BASE / ".py" / "710_launch_certification.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    print('='*80); print('700 PILOT PRODUCTION LAUNCHER RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id,name,cmd in COMMANDS:
        full_cmd=cmd+['--batch-size', str(args.batch_size)]
        if args.execute: full_cmd.append('--execute')
        print('\n>>> '+' '.join(full_cmd)); result=subprocess.run(full_cmd, cwd=str(BASE))
        status='PASS' if result.returncode==0 else 'FAIL'
        if status=='PASS': passed+=1
        else: failed+=1
        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'700 Pilot Production Launcher','batch_size':args.batch_size,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'700_pilot_production_launcher_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('700 PILOT PRODUCTION LAUNCHER SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
