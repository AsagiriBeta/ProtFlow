"""
ProtFlow: A modular pipeline for protein structure prediction, pocket detection, and ligand docking.

This package provides tools for:
- Genome annotation and CDS extraction
- Protein structure prediction using ESM3
- Pocket detection using P2Rank
- Ligand docking using AutoDock Vina
- Biosynthetic gene cluster analysis using antiSMASH
- Structure alignment and comparison
"""

__version__ = "0.2.0"
__author__ = "ProtFlow Contributors"

# Core modules - lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import modules to avoid dependency issues."""
    if name == "antismash":
        from .core import antismash
        return antismash
    elif name == "cds_comparison":
        from .core import cds_comparison
        return cds_comparison
    elif name == "reporting":
        from .core import reporting
        return reporting
    elif name == "esm3_predict":
        from .prediction import esm3_predict
        return esm3_predict
    elif name == "p2rank":
        from .docking import p2rank
        return p2rank
    elif name == "vina_dock":
        from .docking import vina_dock
        return vina_dock
    elif name == "ligand_prep":
        from .docking import ligand_prep
        return ligand_prep
    elif name == "visualization":
        from .visualization import visualization
        return visualization
    elif name in ["config", "exceptions", "logger", "seq_parser"]:
        from .utils import config, exceptions, logger, seq_parser
        return locals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

from ._constants import *

__all__ = [
    "antismash",
    "cds_comparison", 
    "reporting",
    "esm3_predict",
    "p2rank",
    "vina_dock",
    "ligand_prep",
    "visualization",
    "config",
    "exceptions",
    "logger",
    "seq_parser",
    # Constants
    "BASE_DIR",
    "DATA_DIR", 
    "GBK_DIR",
    "PDB_DIR",
    "OUTPUTS_DIR",
]