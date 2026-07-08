import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "218_NeoLegal_AI_Runtime_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "218_1_RuntimeController.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_2_RagRuntimeEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_3_QueryUnderstanding.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_4_LegalAnswerEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_5_CitationEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_6_HallucinationGuard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_7_RuntimeDashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_8_RuntimeDecisionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_9_RuntimeAuditor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "218_10_PublicApiGateway.py"), "--run"],
]
def main():
    print('='*80); print('218 NEOLEGAL AI RUNTIME RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('218 NEOLEGAL AI RUNTIME RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
