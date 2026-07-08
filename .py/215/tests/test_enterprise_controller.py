import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.enterprise_controller.engine import EnterpriseControllerModule
if __name__=='__main__': res=EnterpriseControllerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: enterprise_controller')
