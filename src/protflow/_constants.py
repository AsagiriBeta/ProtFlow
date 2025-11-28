"""Global constants for ProtFlow."""
from pathlib import Path

# Base directories
BASE_DIR = Path.cwd() / "outputs"
DATA_DIR = BASE_DIR / "data"
GBK_DIR = DATA_DIR / "inputs"
PDB_DIR = DATA_DIR / "pdbs"
OUTPUTS_DIR = BASE_DIR

# File extensions
GBK_EXTENSIONS = {".gbk", ".gb", ".genbank"}
PDB_EXTENSIONS = {".pdb", ".ent"}

# Default configuration
DEFAULT_CONFIG_NAME = "protflow_config.json"
DEFAULT_LOG_LEVEL = "INFO"

# Model settings
DEFAULT_ESM3_MODEL = "esm3-sm-open-v1"
DEFAULT_STEPS = 8

# Sequence filtering
MIN_SEQ_LENGTH = 50
MAX_SEQ_LENGTH = 1200
MAX_SEQUENCES = 10

# Docking settings
DEFAULT_VINA_BOX_SIZE = 20
DEFAULT_VINA_EXHAUSTIVENESS = 8
DEFAULT_VINA_NUM_MODES = 9

# P2Rank settings
DEFAULT_P2RANK_VERSION = "2.5.1"
DEFAULT_P2RANK_THREADS = 2