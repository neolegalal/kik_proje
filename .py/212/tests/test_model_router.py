import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.model_router.engine import ModelRouterModule
if __name__=='__main__': res=ModelRouterModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: model_router')
