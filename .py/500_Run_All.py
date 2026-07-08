# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("500", "Production Data Factory SDK", [sys.executable, str(BASE / ".py" / "500_Production_Data_Factory_SDK.py")]),
    ("501", "Data Source Registry", [sys.executable, str(BASE / ".py" / "501_data_source_registry.py")]),
    ("502", "Decision Intake Engine", [sys.executable, str(BASE / ".py" / "502_decision_intake_engine.py")]),
    ("503", "Mass Batch Planner", [sys.executable, str(BASE / ".py" / "503_mass_batch_planner.py")]),
    ("504", "Production Queue Builder", [sys.executable, str(BASE / ".py" / "504_production_queue_builder.py")]),
    ("505", "Quality Gate Binder", [sys.executable, str(BASE / ".py" / "505_quality_gate_binder.py")]),
    ("506", "Parallel Production Controller", [sys.executable, str(BASE / ".py" / "506_parallel_production_controller.py")]),
    ("507", "Data Factory Monitor", [sys.executable, str(BASE / ".py" / "507_data_factory_monitor.py")]),
    ("508", "Data Factory Dashboard", [sys.executable, str(BASE / ".py" / "508_data_factory_dashboard.py")]),
    ("509", "Data Factory Auditor", [sys.executable, str(BASE / ".py" / "509_data_factory_auditor.py")]),
    ("510", "Large Scale Launch Manager", [sys.executable, str(BASE / ".py" / "510_large_scale_launch_manager.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    print('='*80); print('500 PRODUCTION DATA FACTORY RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id,name,cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        status='PASS' if result.returncode==0 else 'FAIL'
        if status=='PASS': passed+=1
        else: failed+=1
        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'500 Production Data Factory','modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'500_production_data_factory_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('500 PRODUCTION DATA FACTORY SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
