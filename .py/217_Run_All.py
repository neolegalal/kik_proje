import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "217_Large_Scale_Production_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "217_1_MassProductionController.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_2_BatchExpansionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_3_ThroughputPlanner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_4_CapacityGovernor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_5_QualityGateManager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_6_ProductionRolloutEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_7_LargeScaleDashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_8_LargeScaleDecisionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_9_LargeScaleAuditor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "217_10_ProductionCompletionManager.py"), "--run"],
]
def main():
    print('='*80); print('217 LARGE SCALE PRODUCTION RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('217 LARGE SCALE PRODUCTION RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
