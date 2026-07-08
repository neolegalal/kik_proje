import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "213_Run_All.py")],
    [sys.executable, str(BASE / ".py" / "214_Run_All.py")],
    [sys.executable, str(BASE / ".py" / "215_Run_All.py")],
    [sys.executable, str(BASE / ".py" / "216_Run_All.py")],
    [sys.executable, str(BASE / ".py" / "217_Run_All.py")],
    [sys.executable, str(BASE / ".py" / "218_Run_All.py")],
]
def main():
    print('='*80); print('213-218 MEGA PLATFORM RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('213-218 MEGA PLATFORM RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
