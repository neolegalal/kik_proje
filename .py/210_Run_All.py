# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "210_Self_Healing_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "210_1_Recovery_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_2_Retry_Manager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_3_Root_Cause_Analyzer.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_4_Auto_Repair_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_5_Isolation_Manager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_6_Rollback_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_7_Resume_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_8_Healing_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_9_Self_Healing_Decision_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "210_10_Healing_Auditor.py"), "--run"],
]

def main():
    print("=" * 80)
    print("210 SELF-HEALING RUN ALL BAŞLADI")
    print("=" * 80)
    for cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0:
            print("HATA:", " ".join(cmd))
            sys.exit(result.returncode)
    print("\n" + "=" * 80)
    print("210 SELF-HEALING RUN ALL TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    main()
