import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.public_api_gateway.engine import PublicApiGatewayModule
if __name__=='__main__': res=PublicApiGatewayModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: public_api_gateway')
