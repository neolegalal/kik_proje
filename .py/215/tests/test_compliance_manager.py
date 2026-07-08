import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.compliance_manager.engine import ComplianceManagerModule
if __name__=='__main__': res=ComplianceManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: compliance_manager')
