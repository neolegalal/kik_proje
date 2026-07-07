# -*- coding: utf-8 -*-
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent / "206"
sys.path.insert(0, str(PACKAGE_DIR))

from priority_queue_manager import main

if __name__ == "__main__":
    main()
