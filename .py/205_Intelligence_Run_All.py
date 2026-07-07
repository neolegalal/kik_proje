# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "205_1_Production_Analytics.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_2_Queue_Intelligence.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_3_Worker_Intelligence.py")],
    [sys.executable, str(BASE / ".py" / "205_4_DB_Growth_Analytics.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_5_Event_Intelligence.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_6_Logger_Intelligence.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_7_Platform_Stability.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_8_Health_Trend.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_9_Forecast_Engine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "205_10_Executive_AI_Summary.py"), "--run"],
]

def main():
    print("="*80)
    print("205 INTELLIGENCE RUN ALL BAŞLADI")
    print("="*80)
    for cmd in COMMANDS:
        print("\\n>>>", " ".join(cmd))
        r = subprocess.run(cmd, cwd=str(BASE))
        if r.returncode != 0:
            print("HATA:", " ".join(cmd))
            sys.exit(r.returncode)
    print("\\n" + "="*80)
    print("205 INTELLIGENCE RUN ALL TAMAMLANDI")
    print("="*80)

if __name__ == "__main__":
    main()
