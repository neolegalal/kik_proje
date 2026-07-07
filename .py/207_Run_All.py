# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")

COMMANDS = [
    [sys.executable, str(BASE / ".py" / "207_Execution_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "207_1_Batch_Executor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_2_Worker_Dispatcher.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_3_Queue_Executor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_4_Retry_Executor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_5_Recovery_Executor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_6_Parallel_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_7_Pipeline_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_8_Execution_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_9_Execution_Decision_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "207_10_Execution_Auditor.py"), "--run"],
]

def main():
    print("=" * 80)
    print("207 EXECUTION RUN ALL BAŞLADI")
    print("=" * 80)

    for cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0:
            print("HATA:", " ".join(cmd))
            sys.exit(result.returncode)

    print("\n" + "=" * 80)
    print("207 EXECUTION RUN ALL TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    main()
