import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.cluster_auditor.engine import ClusterAuditorModule
if __name__=='__main__': res=ClusterAuditorModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: cluster_auditor')
