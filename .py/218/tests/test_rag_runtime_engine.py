import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.rag_runtime_engine.engine import RagRuntimeEngineModule
if __name__=='__main__': res=RagRuntimeEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: rag_runtime_engine')
