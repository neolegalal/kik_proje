import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.query_understanding.engine import QueryUnderstandingModule
if __name__=='__main__': res=QueryUnderstandingModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: query_understanding')
