import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.mass_production_controller.engine import MassProductionControllerModule
if __name__=='__main__': res=MassProductionControllerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: mass_production_controller')
