import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.worker_pool_manager.engine import WorkerPoolManagerModule
if __name__=='__main__': res=WorkerPoolManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: worker_pool_manager')
