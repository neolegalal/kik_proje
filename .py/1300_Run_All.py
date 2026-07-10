# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1300", "Legal Advisory Intelligence SDK", [sys.executable, str(BASE / ".py" / "1300_Legal_Advisory_Intelligence_SDK.py")]),
    ("1301", "Case Intake Analyzer", [sys.executable, str(BASE / ".py" / "1301_case_intake_analyzer.py")]),
    ("1302", "Claim Defense Mapper", [sys.executable, str(BASE / ".py" / "1302_claim_defense_mapper.py")]),
    ("1303", "Legal Basis Finder", [sys.executable, str(BASE / ".py" / "1303_legal_basis_finder.py")]),
    ("1304", "Precedent Strength Analyzer", [sys.executable, str(BASE / ".py" / "1304_precedent_strength_analyzer.py")]),
    ("1305", "Outcome Probability Scorer", [sys.executable, str(BASE / ".py" / "1305_outcome_probability_scorer.py")]),
    ("1306", "Defense Draft Generator", [sys.executable, str(BASE / ".py" / "1306_defense_draft_generator.py")]),
    ("1307", "Complaint Appeal Draft Generator", [sys.executable, str(BASE / ".py" / "1307_complaint_appeal_draft_generator.py")]),
    ("1308", "Court Application Risk Analyzer", [sys.executable, str(BASE / ".py" / "1308_court_application_risk_analyzer.py")]),
    ("1309", "Strategy Recommendation Engine", [sys.executable, str(BASE / ".py" / "1309_strategy_recommendation_engine.py")]),
    ("1310", "Advisory Quality Auditor", [sys.executable, str(BASE / ".py" / "1310_advisory_quality_auditor.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-text', default=None)
    parser.add_argument('--advisory-type', default='general')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1300 LEGAL ADVISORY INTELLIGENCE RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ['--advisory-type', args.advisory_type]
        if args.case_text: full += ['--case-text', args.case_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1300 Legal Advisory Intelligence','advisory_type':args.advisory_type,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1300_legal_advisory_intelligence_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1300 LEGAL ADVISORY INTELLIGENCE SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
