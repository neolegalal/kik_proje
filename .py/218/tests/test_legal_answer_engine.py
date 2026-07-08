import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.legal_answer_engine.engine import LegalAnswerEngineModule
if __name__=='__main__': res=LegalAnswerEngineModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: legal_answer_engine')
