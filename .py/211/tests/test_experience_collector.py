import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.experience_collector.engine import ExperienceCollectorModule
if __name__=='__main__': res=ExperienceCollectorModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: experience_collector')
