import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.cluster_recovery_manager.engine import ClusterRecoveryManagerModule
if __name__=='__main__': res=ClusterRecoveryManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: cluster_recovery_manager')
