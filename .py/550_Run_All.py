# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("550", "Production Factory Runtime SDK", [sys.executable, str(BASE / ".py" / "550_Production_Factory_Runtime_SDK.py")]),
    ("551", "Runtime Queue Manager", [sys.executable, str(BASE / ".py" / "551_runtime_queue_manager.py")]),
    ("552", "Worker Pool Runtime", [sys.executable, str(BASE / ".py" / "552_worker_pool_runtime.py")]),
    ("553", "Multi API Runtime", [sys.executable, str(BASE / ".py" / "553_multi_api_runtime.py")]),
    ("554", "Parallel Producer", [sys.executable, str(BASE / ".py" / "554_parallel_producer.py")]),
    ("555", "Token Manager", [sys.executable, str(BASE / ".py" / "555_token_manager.py")]),
    ("556", "Cost Optimizer", [sys.executable, str(BASE / ".py" / "556_cost_optimizer.py")]),
    ("557", "Resume Runtime", [sys.executable, str(BASE / ".py" / "557_resume_runtime.py")]),
    ("558", "Batch Executor Runtime", [sys.executable, str(BASE / ".py" / "558_batch_executor_runtime.py")]),
    ("559", "Live Runtime Dashboard", [sys.executable, str(BASE / ".py" / "559_live_runtime_dashboard.py")]),
    ("560", "Runtime Auditor", [sys.executable, str(BASE / ".py" / "560_runtime_auditor.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    print('='*80); print('550 PRODUCTION FACTORY RUNTIME RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id,name,cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        status='PASS' if result.returncode==0 else 'FAIL'
        if status=='PASS': passed+=1
        else: failed+=1
        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'550 Production Factory Runtime','modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'550_production_factory_runtime_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('550 PRODUCTION FACTORY RUNTIME SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
