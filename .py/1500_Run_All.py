# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1500", "Legal Reasoning Engine SDK", [sys.executable, str(BASE / ".py" / "1500_Legal_Reasoning_Engine_SDK.py")]),
    ("1501", "Issue Identifier", [sys.executable, str(BASE / ".py" / "1501_issue_identifier.py")]),
    ("1502", "Legal Argument Generator", [sys.executable, str(BASE / ".py" / "1502_legal_argument_generator.py")]),
    ("1503", "Counter Argument Generator", [sys.executable, str(BASE / ".py" / "1503_counter_argument_generator.py")]),
    ("1504", "Evidence Weight Analyzer", [sys.executable, str(BASE / ".py" / "1504_evidence_weight_analyzer.py")]),
    ("1505", "Precedent Comparator", [sys.executable, str(BASE / ".py" / "1505_precedent_comparator.py")]),
    ("1506", "Legal Conflict Resolver", [sys.executable, str(BASE / ".py" / "1506_legal_conflict_resolver.py")]),
    ("1507", "Outcome Prediction Engine", [sys.executable, str(BASE / ".py" / "1507_outcome_prediction_engine.py")]),
    ("1508", "Strategy Optimizer", [sys.executable, str(BASE / ".py" / "1508_strategy_optimizer.py")]),
    ("1509", "AI Reasoning Auditor", [sys.executable, str(BASE / ".py" / "1509_ai_reasoning_auditor.py")]),
    ("1510", "Legal Reasoning Certificate", [sys.executable, str(BASE / ".py" / "1510_legal_reasoning_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-text', default=None)
    parser.add_argument('--reasoning-type', default='general')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1500 LEGAL REASONING ENGINE RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ['--reasoning-type', args.reasoning_type]
        if args.case_text: full += ['--case-text', args.case_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1500 Legal Reasoning Engine','reasoning_type':args.reasoning_type,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1500_legal_reasoning_engine_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1500 LEGAL REASONING ENGINE SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
