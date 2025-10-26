# Lightweight package init for esm3_pipeline
from pathlib import Path

# Default base dir mirrors the notebook's logic
COLAB_BASE = Path('/content/esm3_pipeline')
BASE = COLAB_BASE if COLAB_BASE.exists() else (Path.cwd() / 'esm3_pipeline')

GBK_DIR = BASE / 'gbk_input'
PDB_DIR = BASE / 'pdbs'
DATA_DIR = BASE / 'data'
OUT_DIR = BASE / 'outputs'

for d in (BASE, GBK_DIR, PDB_DIR, DATA_DIR, OUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

__all__ = [
    'BASE', 'GBK_DIR', 'PDB_DIR', 'DATA_DIR', 'OUT_DIR'
]

