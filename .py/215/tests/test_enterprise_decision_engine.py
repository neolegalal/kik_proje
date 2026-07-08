import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.enterprise_decision_engine.engine import EnterpriseDecisionEngineModule
if __name__=='__main__': res=EnterpriseDecisionEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: enterprise_decision_engine')
