# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1970-1990", "Case Graph Trainer SDK", [sys.executable, str(BASE / ".py" / "1970_1990_Case_Graph_Trainer_SDK.py")]),
    ("1971", "Dispute Priority Scorer", [sys.executable, str(BASE / ".py" / "1971_dispute_priority_scorer.py")]),
    ("1972", "Main Issue Detector", [sys.executable, str(BASE / ".py" / "1972_main_issue_detector.py")]),
    ("1973", "Sub Issue Mapper", [sys.executable, str(BASE / ".py" / "1973_sub_issue_mapper.py")]),
    ("1974", "Result Impact Analyzer", [sys.executable, str(BASE / ".py" / "1974_result_impact_analyzer.py")]),
    ("1975", "Case Intelligence Auditor", [sys.executable, str(BASE / ".py" / "1975_case_intelligence_auditor.py")]),
    ("1981", "Graph Node Builder", [sys.executable, str(BASE / ".py" / "1981_graph_node_builder.py")]),
    ("1982", "Graph Edge Builder", [sys.executable, str(BASE / ".py" / "1982_graph_edge_builder.py")]),
    ("1983", "Precedent Relation Builder", [sys.executable, str(BASE / ".py" / "1983_precedent_relation_builder.py")]),
    ("1984", "Contradiction Relation Builder", [sys.executable, str(BASE / ".py" / "1984_contradiction_relation_builder.py")]),
    ("1985", "Legal Graph Auditor", [sys.executable, str(BASE / ".py" / "1985_legal_graph_auditor.py")]),
    ("1991", "Instruction Dataset Builder", [sys.executable, str(BASE / ".py" / "1991_instruction_dataset_builder.py")]),
    ("1992", "Rag Dataset Builder", [sys.executable, str(BASE / ".py" / "1992_rag_dataset_builder.py")]),
    ("1993", "Fine Tuning Dataset Builder", [sys.executable, str(BASE / ".py" / "1993_fine_tuning_dataset_builder.py")]),
    ("1994", "Evaluation Benchmark Builder", [sys.executable, str(BASE / ".py" / "1994_evaluation_benchmark_builder.py")]),
    ("1995", "AI Trainer Certificate", [sys.executable, str(BASE / ".py" / "1995_ai_trainer_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--master-record', default=None)
    parser.add_argument('--case-text', default=None)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1970-1990 CASE GRAPH TRAINER RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = list(cmd)
        if args.master_record: full += ['--master-record', args.master_record]
        if args.case_text: full += ['--case-text', args.case_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1970-1990 Case Graph Trainer','execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1970_1990_case_graph_trainer_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1970-1990 CASE GRAPH TRAINER SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
