import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.improvement_dashboard.engine import ImprovementDashboardModule
if __name__=='__main__': res=ImprovementDashboardModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: improvement_dashboard')
