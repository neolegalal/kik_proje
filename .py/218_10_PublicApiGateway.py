import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "218"
sys.path.insert(0, str(PACKAGE_DIR))
from public_api_gateway_manager import main
if __name__=='__main__': main()
