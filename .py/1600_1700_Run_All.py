# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1600", "NeoLegal Expert Orchestrator SDK", [sys.executable, str(BASE / ".py" / "1600_NeoLegal_Expert_Orchestrator_SDK.py")]),
    ("1601", "Case Intake Orchestrator", [sys.executable, str(BASE / ".py" / "1601_case_intake_orchestrator.py")]),
    ("1602", "Decision Retrieval Orchestrator", [sys.executable, str(BASE / ".py" / "1602_decision_retrieval_orchestrator.py")]),
    ("1603", "Advisory Orchestrator", [sys.executable, str(BASE / ".py" / "1603_advisory_orchestrator.py")]),
    ("1604", "Litigation Orchestrator", [sys.executable, str(BASE / ".py" / "1604_litigation_orchestrator.py")]),
    ("1605", "Legal Reasoning Orchestrator", [sys.executable, str(BASE / ".py" / "1605_legal_reasoning_orchestrator.py")]),
    ("1606", "Conflict Resolver", [sys.executable, str(BASE / ".py" / "1606_conflict_resolver.py")]),
    ("1607", "Final Legal Opinion Generator", [sys.executable, str(BASE / ".py" / "1607_final_legal_opinion_generator.py")]),
    ("1608", "Action Plan Generator", [sys.executable, str(BASE / ".py" / "1608_action_plan_generator.py")]),
    ("1609", "Expert Quality Auditor", [sys.executable, str(BASE / ".py" / "1609_expert_quality_auditor.py")]),
    ("1610", "NeoLegal Expert Certificate", [sys.executable, str(BASE / ".py" / "1610_neolegal_expert_certificate.py")]),
    ("1700", "Client Workspace Memory SDK", [sys.executable, str(BASE / ".py" / "1700_Client_Workspace_Memory_SDK.py")]),
    ("1701", "Client Profile Manager", [sys.executable, str(BASE / ".py" / "1701_client_profile_manager.py")]),
    ("1702", "Case Workspace Manager", [sys.executable, str(BASE / ".py" / "1702_case_workspace_manager.py")]),
    ("1703", "Conversation Memory Manager", [sys.executable, str(BASE / ".py" / "1703_conversation_memory_manager.py")]),
    ("1704", "Document Memory Indexer", [sys.executable, str(BASE / ".py" / "1704_document_memory_indexer.py")]),
    ("1705", "Strategy History Tracker", [sys.executable, str(BASE / ".py" / "1705_strategy_history_tracker.py")]),
    ("1706", "Deadline Reminder Planner", [sys.executable, str(BASE / ".py" / "1706_deadline_reminder_planner.py")]),
    ("1707", "Task Action Board", [sys.executable, str(BASE / ".py" / "1707_task_action_board.py")]),
    ("1708", "Knowledge Memory Retriever", [sys.executable, str(BASE / ".py" / "1708_knowledge_memory_retriever.py")]),
    ("1709", "Workspace Dashboard", [sys.executable, str(BASE / ".py" / "1709_workspace_dashboard.py")]),
    ("1710", "Workspace Quality Auditor", [sys.executable, str(BASE / ".py" / "1710_workspace_quality_auditor.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-text', default=None)
    parser.add_argument('--expert-mode', default='general')
    parser.add_argument('--client-name', default='Pilot Client')
    parser.add_argument('--case-name', default='Pilot Procurement Case')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1600-1700 NEOLEGAL EXPERT WORKSPACE RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = list(cmd)
        if module_id.startswith('16'):
            full += ['--expert-mode', args.expert_mode]
            if args.case_text: full += ['--case-text', args.case_text]
        else:
            full += ['--client-name', args.client_name, '--case-name', args.case_name]
            if args.case_text: full += ['--case-text', args.case_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1600-1700 NeoLegal Expert Workspace','execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1600_1700_neolegal_expert_workspace_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1600-1700 NEOLEGAL EXPERT WORKSPACE SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(44)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
