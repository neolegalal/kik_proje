import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.context_builder.engine import ContextBuilderModule
if __name__=='__main__': res=ContextBuilderModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: context_builder')
