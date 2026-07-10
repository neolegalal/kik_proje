# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1400", "Litigation Intelligence Platform SDK", [sys.executable, str(BASE / ".py" / "1400_Litigation_Intelligence_Platform_SDK.py")]),
    ("1401", "Complaint Draft Engine", [sys.executable, str(BASE / ".py" / "1401_complaint_draft_engine.py")]),
    ("1402", "Appeal Draft Engine", [sys.executable, str(BASE / ".py" / "1402_appeal_draft_engine.py")]),
    ("1403", "Administrative Case Draft Engine", [sys.executable, str(BASE / ".py" / "1403_administrative_case_draft_engine.py")]),
    ("1404", "Defense Reply Engine", [sys.executable, str(BASE / ".py" / "1404_defense_reply_engine.py")]),
    ("1405", "Counter Defense Analyzer", [sys.executable, str(BASE / ".py" / "1405_counter_defense_analyzer.py")]),
    ("1406", "Evidence Gap Analyzer", [sys.executable, str(BASE / ".py" / "1406_evidence_gap_analyzer.py")]),
    ("1407", "Stay Of Execution Analyzer", [sys.executable, str(BASE / ".py" / "1407_stay_of_execution_analyzer.py")]),
    ("1408", "Hearing Strategy Planner", [sys.executable, str(BASE / ".py" / "1408_hearing_strategy_planner.py")]),
    ("1409", "Litigation Probability Updater", [sys.executable, str(BASE / ".py" / "1409_litigation_probability_updater.py")]),
    ("1410", "Litigation Quality Auditor", [sys.executable, str(BASE / ".py" / "1410_litigation_quality_auditor.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-text', default=None)
    parser.add_argument('--litigation-type', default='general')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1400 LITIGATION INTELLIGENCE PLATFORM RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ['--litigation-type', args.litigation_type]
        if args.case_text: full += ['--case-text', args.case_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1400 Litigation Intelligence Platform','litigation_type':args.litigation_type,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1400_litigation_intelligence_platform_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1400 LITIGATION INTELLIGENCE PLATFORM SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(44)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
