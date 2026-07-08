# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "209_Autonomous_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "209_1_Autonomous_Controller.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_2_Policy_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_3_Risk_Gate.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_4_Auto_Approval_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_5_Auto_Pause_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_6_Auto_Resume_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_7_Operations_Feedback_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_8_Governance_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_9_Autonomous_Decision_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "209_10_Operations_Auditor.py"), "--run"],
]

def main():
    print("=" * 80)
    print("209 AUTONOMOUS OPERATIONS RUN ALL BAŞLADI")
    print("=" * 80)
    for cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0:
            print("HATA:", " ".join(cmd))
            sys.exit(result.returncode)
    print("\n" + "=" * 80)
    print("209 AUTONOMOUS OPERATIONS RUN ALL TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    main()
