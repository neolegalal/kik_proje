import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "216_Production_Cluster_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "216_1_ClusterController.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_2_NodeRegistry.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_3_WorkerPoolManager.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_4_LoadBalancer.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_5_ClusterHealthMonitor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_6_ScalingPlanner.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_7_ClusterDashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_8_ClusterDecisionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_9_ClusterAuditor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "216_10_ClusterRecoveryManager.py"), "--run"],
]
def main():
    print('='*80); print('216 PRODUCTION CLUSTER RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('216 PRODUCTION CLUSTER RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
