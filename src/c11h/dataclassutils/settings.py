from pathlib import Path, PurePath

# good to know
ROOT_DIR = PurePath(__file__).parent
CWD = Path.cwd()

# parse version file
try:
    with open(ROOT_DIR / 'VERSION') as f:
        VERSION = f.read().strip()
except (OSError, IOError):
    VERSION = '0.0.0'
