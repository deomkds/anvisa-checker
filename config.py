import os
import sys
from pathlib import Path

DEBUG_MODE = True
VERBOSE = DEBUG_MODE

home_dir = Path.home()
dest_path = os.path.join(home_dir, "Desktop/")

OS = sys.platform