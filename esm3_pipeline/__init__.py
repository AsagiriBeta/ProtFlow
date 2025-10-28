"""
ProtFlow: Modular pipeline for protein structure prediction and analysis.

This package provides tools for:
- Parsing GenBank files
- Predicting protein structures with ESM3
- Detecting binding pockets with P2Rank
- Preparing ligands and docking with AutoDock Vina
- Running antiSMASH analysis
- Generating comprehensive reports
"""
from pathlib import Path

__version__ = "0.2.0"
__author__ = "ProtFlow Contributors"

# Default base dir mirrors the notebook's logic
COLAB_BASE = Path('/content/esm3_pipeline')
BASE = COLAB_BASE if COLAB_BASE.exists() else (Path.cwd() / 'esm3_pipeline')

GBK_DIR = BASE / 'gbk_input'
PDB_DIR = BASE / 'pdbs'
DATA_DIR = BASE / 'data'
OUT_DIR = BASE / 'outputs'

for d in (BASE, GBK_DIR, PDB_DIR, DATA_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Import core functionality
from . import config
from . import exceptions
from . import logger
from . import seq_parser
from . import esm3_predict
from . import p2rank
from . import ligand_prep
from . import vina_dock
from . import reporting

__all__ = [
    # Version info
    '__version__',
    '__author__',

    # Paths
    'BASE',
    'GBK_DIR',
    'PDB_DIR',
    'DATA_DIR',
    'OUT_DIR',

    # Modules
    'config',
    'exceptions',
    'logger',
    'seq_parser',
    'esm3_predict',
    'p2rank',
    'ligand_prep',
    'vina_dock',
    'reporting',
]



