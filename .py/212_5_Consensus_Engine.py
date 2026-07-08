import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "212"
sys.path.insert(0, str(PACKAGE_DIR))
from consensus_engine_manager import main
if __name__=='__main__': main()
