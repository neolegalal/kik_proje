import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.tenant_manager.engine import TenantManagerModule
if __name__=='__main__': res=TenantManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: tenant_manager')
