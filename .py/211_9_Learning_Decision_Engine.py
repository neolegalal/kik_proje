import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "211"
sys.path.insert(0, str(PACKAGE_DIR))
from learning_decision_engine_manager import main
if __name__=='__main__': main()
