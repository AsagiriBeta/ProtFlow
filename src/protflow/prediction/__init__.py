"""Protein structure prediction modules."""

# Lazy imports to avoid dependency issues
def __getattr__(name):
    """Lazy import modules to avoid torch dependency issues."""
    if name in ["ESM3Predictor", "predict_structures", "validate_sequences"]:
        from .esm3_predict import ESM3Predictor, predict_structures, validate_sequences
        return locals()[name]
    elif name in ["DaliAligner", "DaliResult", "run_dali_alignment", "batch_align"]:
        from .dali import DaliAligner, DaliResult, run_dali_alignment, batch_align
        return locals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "ESM3Predictor",
    "predict_structures",
    "validate_sequences",
    # DALI structure alignment
    "DaliAligner",
    "DaliResult",
    "run_dali_alignment",
    "batch_align",
]