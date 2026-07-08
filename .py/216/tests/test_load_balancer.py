import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.load_balancer.engine import LoadBalancerModule
if __name__=='__main__': res=LoadBalancerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: load_balancer')
