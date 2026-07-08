import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.production_completion_manager.engine import ProductionCompletionManagerModule
if __name__=='__main__': res=ProductionCompletionManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: production_completion_manager')
