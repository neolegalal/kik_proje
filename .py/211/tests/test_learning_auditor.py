import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.learning_auditor.engine import LearningAuditorModule
if __name__=='__main__': res=LearningAuditorModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: learning_auditor')
