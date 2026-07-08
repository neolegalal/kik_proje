import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.multi_model_engine.engine import MultiModelEngineModule
if __name__=='__main__': res=MultiModelEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: multi_model_engine')
