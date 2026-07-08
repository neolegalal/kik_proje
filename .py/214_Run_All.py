import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "214_Continuous_Improvement_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "214_1_ImprovementCollector.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_2_FeedbackAnalyzer.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_3_QualityLoopEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_4_OptimizationPlanner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_5_ImprovementPrioritizer.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_6_ExperimentManager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_7_ImprovementDashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_8_ImprovementDecisionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_9_ImprovementAuditor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "214_10_ImprovementRoadmapEngine.py"), "--run"],
]
def main():
    print('='*80); print('214 CONTINUOUS IMPROVEMENT RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('214 CONTINUOUS IMPROVEMENT RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
