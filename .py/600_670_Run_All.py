# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("600", "Intelligent Production Engine SDK", [sys.executable, str(BASE / ".py" / "600_Intelligent_Production_Engine_SDK.py")]),
    ("600", "Intelligent Production Controller", [sys.executable, str(BASE / ".py" / "600_intelligent_production_controller.py")]),
    ("610", "Smart Batch Optimizer", [sys.executable, str(BASE / ".py" / "610_smart_batch_optimizer.py")]),
    ("620", "AI Cost Token Optimizer", [sys.executable, str(BASE / ".py" / "620_ai_cost_token_optimizer.py")]),
    ("630", "Distributed Worker Cluster", [sys.executable, str(BASE / ".py" / "630_distributed_worker_cluster.py")]),
    ("640", "Production Knowledge Cache", [sys.executable, str(BASE / ".py" / "640_production_knowledge_cache.py")]),
    ("650", "Production Analytics Center", [sys.executable, str(BASE / ".py" / "650_production_analytics_center.py")]),
    ("660", "Human Review Workflow", [sys.executable, str(BASE / ".py" / "660_human_review_workflow.py")]),
    ("670", "Continuous Improvement Engine", [sys.executable, str(BASE / ".py" / "670_continuous_improvement_engine.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    print('='*80); print('600-670 INTELLIGENT PRODUCTION ENGINE RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id,name,cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        status='PASS' if result.returncode==0 else 'FAIL'
        if status=='PASS': passed+=1
        else: failed+=1
        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'v4.0 Intelligent Production Engine','modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'600_670_intelligent_production_engine_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('600-670 INTELLIGENT PRODUCTION ENGINE SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(45)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
