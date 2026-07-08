import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.large_scale_dashboard.engine import LargeScaleDashboardModule
if __name__=='__main__': res=LargeScaleDashboardModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: large_scale_dashboard')
