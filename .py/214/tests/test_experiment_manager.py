import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.experiment_manager.engine import ExperimentManagerModule
if __name__=='__main__': res=ExperimentManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: experiment_manager')
