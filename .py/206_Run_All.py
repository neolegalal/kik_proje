# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")

COMMANDS = [
    [sys.executable, str(BASE / ".py" / "206_Scheduler_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "206_1_Scheduler_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_2_Job_Planner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_3_Priority_Queue.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_4_Dependency_Resolver.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_5_Retry_Scheduler.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_6_Cron_Manager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_7_Batch_Planner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_8_Scheduler_Dashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "206_9_Scheduler_Decision_Engine.py"), "--run"],
]

def main():
    print("=" * 80)
    print("206 SCHEDULER RUN ALL BAŞLADI")
    print("=" * 80)

    for cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0:
            print("HATA:", " ".join(cmd))
            sys.exit(result.returncode)

    print("\n" + "=" * 80)
    print("206 SCHEDULER RUN ALL TAMAMLANDI")
    print("=" * 80)

if __name__ == "__main__":
    main()
