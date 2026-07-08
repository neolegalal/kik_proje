import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "217"
sys.path.insert(0, str(PACKAGE_DIR))
from quality_gate_manager_manager import main
if __name__=='__main__': main()
