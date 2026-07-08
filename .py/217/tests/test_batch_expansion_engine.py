import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.batch_expansion_engine.engine import BatchExpansionEngineModule
if __name__=='__main__': res=BatchExpansionEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: batch_expansion_engine')
