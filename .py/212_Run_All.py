import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "212_AI_Orchestrator_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "212_1_Model_Router.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_2_Prompt_Planner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_3_AI_Task_Manager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_4_Multi_Model_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_5_Consensus_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_6_Response_Optimizer.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_7_AI_Supervisor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_8_AI_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_9_AI_Decision_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "212_10_AI_Auditor.py"), "--run"],
]
def main():
    print('='*80); print('212 AI ORCHESTRATOR RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('212 AI ORCHESTRATOR RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
