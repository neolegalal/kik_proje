import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.service_catalog.engine import ServiceCatalogModule
if __name__=='__main__': res=ServiceCatalogModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: service_catalog')
