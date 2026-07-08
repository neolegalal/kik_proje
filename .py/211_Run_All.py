import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "211_Learning_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "211_1_Experience_Collector.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_2_Pattern_Learner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_3_Failure_Learner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_4_Success_Learner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_5_Worker_Learning.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_6_Batch_Learning.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_7_Recommendation_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_8_Learning_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_9_Learning_Decision_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "211_10_Learning_Auditor.py"), "--run"],
]
def main():
    print('='*80); print('211 LEARNING RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('211 LEARNING RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
