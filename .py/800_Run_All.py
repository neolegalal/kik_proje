# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("800", "Real Production Engine SDK", [sys.executable, str(BASE / ".py" / "800_Real_Production_Engine_SDK.py")]),
    ("801", "Real Batch Selector", [sys.executable, str(BASE / ".py" / "801_real_batch_selector.py")]),
    ("802", "Real Queue Builder", [sys.executable, str(BASE / ".py" / "802_real_queue_builder.py")]),
    ("803", "Production Chain Binder", [sys.executable, str(BASE / ".py" / "803_production_chain_binder.py")]),
    ("804", "Quality Chain Executor", [sys.executable, str(BASE / ".py" / "804_quality_chain_executor.py")]),
    ("805", "Legal Accuracy Gate", [sys.executable, str(BASE / ".py" / "805_legal_accuracy_gate.py")]),
    ("806", "Acceptance Import Export Runner", [sys.executable, str(BASE / ".py" / "806_acceptance_import_export_runner.py")]),
    ("807", "Real Production Metrics", [sys.executable, str(BASE / ".py" / "807_real_production_metrics.py")]),
    ("808", "Real Production Dashboard", [sys.executable, str(BASE / ".py" / "808_real_production_dashboard.py")]),
    ("809", "Real Production Auditor", [sys.executable, str(BASE / ".py" / "809_real_production_auditor.py")]),
    ("810", "Real Production Launch Certificate", [sys.executable, str(BASE / ".py" / "810_real_production_launch_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    print('='*80); print('800 REAL PRODUCTION ENGINE RUN ALL BASLADI'); print('='*80)
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
    payload={'created_at':now_text(),'program':'800 Real Production Engine','batch_size':args.batch_size,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'800_real_production_engine_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('800 REAL PRODUCTION ENGINE SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(45)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
