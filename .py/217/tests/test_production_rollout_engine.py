import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.production_rollout_engine.engine import ProductionRolloutEngineModule
if __name__=='__main__': res=ProductionRolloutEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: production_rollout_engine')
