import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.runtime_decision_engine.engine import RuntimeDecisionEngineModule
if __name__=='__main__': res=RuntimeDecisionEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: runtime_decision_engine')
