import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.ai_dashboard.engine import AiDashboardModule
if __name__=='__main__': res=AiDashboardModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: ai_dashboard')
