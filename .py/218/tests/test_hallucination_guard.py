import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.hallucination_guard.engine import HallucinationGuardModule
if __name__=='__main__': res=HallucinationGuardModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: hallucination_guard')
