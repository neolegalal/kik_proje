import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.response_optimizer.engine import ResponseOptimizerModule
if __name__=='__main__': res=ResponseOptimizerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: response_optimizer')
