import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.ai_task_manager.engine import AiTaskManagerModule
if __name__=='__main__': res=AiTaskManagerModule().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: ai_task_manager')
