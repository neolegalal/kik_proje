import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.batch_learning.engine import BatchLearningModule
if __name__=='__main__': res=BatchLearningModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: batch_learning')
