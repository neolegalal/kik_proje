import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "215_Enterprise_Platform_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "215_1_EnterpriseController.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_2_TenantManager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_3_AccessGovernance.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_4_PolicyRegistry.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_5_ServiceCatalog.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_6_ComplianceManager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_7_EnterpriseDashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_8_EnterpriseDecisionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_9_EnterpriseAuditor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "215_10_EnterpriseReleaseManager.py"), "--run"],
]
def main():
    print('='*80); print('215 ENTERPRISE PLATFORM RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('215 ENTERPRISE PLATFORM RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
