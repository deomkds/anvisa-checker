import os
from pathlib import Path

DEBUG_MODE = True
VERBOSE = DEBUG_MODE

home_dir = Path.home()
src_path = os.path.join(home_dir, "Desktop/")