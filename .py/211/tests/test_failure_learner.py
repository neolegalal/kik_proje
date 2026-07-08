import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.failure_learner.engine import FailureLearnerModule
if __name__=='__main__': res=FailureLearnerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: failure_learner')
