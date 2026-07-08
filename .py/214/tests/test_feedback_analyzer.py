import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.feedback_analyzer.engine import FeedbackAnalyzerModule
if __name__=='__main__': res=FeedbackAnalyzerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: feedback_analyzer')
