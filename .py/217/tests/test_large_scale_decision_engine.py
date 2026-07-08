import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.large_scale_decision_engine.engine import LargeScaleDecisionEngineModule
if __name__=='__main__': res=LargeScaleDecisionEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: large_scale_decision_engine')
