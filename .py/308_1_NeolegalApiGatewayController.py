import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "308"
sys.path.insert(0, str(PACKAGE_DIR))
from neolegal_api_gateway_controller_manager import main
if __name__=='__main__': main()
