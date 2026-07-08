# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "208_Automation_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "208_1_Automation_Controller.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_2_Trigger_Manager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_3_Safe_Run_Gate.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_4_Execution_Trigger.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_5_Metrics_Refresh_Automation.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_6_Intelligence_Refresh_Automation.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_7_Scheduler_Feedback_Automation.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_8_Notification_Automation.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_9_Automation_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "208_10_Automation_Auditor.py"), "--run"],
]

def main():
    print("=" * 80)
    print("208 AUTOMATION RUN ALL BAŞLADI")
    print("=" * 80)
    for cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0:
            print("HATA:", " ".join(cmd))
            sys.exit(result.returncode)
    print("\n" + "=" * 80)
    print("208 AUTOMATION RUN ALL TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    main()
