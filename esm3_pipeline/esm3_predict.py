"""
ESM3 structure prediction utilities with caching and progress tracking.
"""
from pathlib import Path
from typing import Iterable, Optional, Tuple, Any
import hashlib
import pickle

import torch
from tqdm import tqdm

from .logger import get_logger
from .exceptions import ModelLoadError, PredictionError

logger = get_logger(__name__)

# Global model cache
_model_cache: Optional[Tuple[Any, str]] = None


def load_esm3_small(
    device: Optional[str] = None,
    model_name: str = 'esm3-sm-open-v1',
    use_cache: bool = True
) -> Tuple[Any, str]:
    """
    Load ESM3 small model with caching support.

    Args:
        device: Target device ('cuda', 'cpu', 'mps', or None for auto-detect)
        model_name: Model identifier from HuggingFace
        use_cache: Use cached model if available

    Returns:
        Tuple of (model, device)

    Raises:
        ModelLoadError: If model loading fails
    """
    global _model_cache

    # Return cached model if available
    if use_cache and _model_cache is not None:
        logger.info("Using cached ESM3 model")
        return _model_cache

    try:
        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = 'cuda'
                logger.info("CUDA available, using GPU")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device = 'mps'
                logger.info("MPS available, using Apple Silicon GPU")
            else:
                device = 'cpu'
                logger.info("Using CPU")

        logger.info(f"Loading ESM3 model: {model_name}")

        # Lazy import to avoid loading if not needed
        from esm.models.esm3 import ESM3

        model = ESM3.from_pretrained(model_name).to(device)
        model.eval()  # Set to evaluation mode

        logger.info(f"Model loaded successfully on {device}")

        # Cache the model
        if use_cache:
            _model_cache = (model, device)

        return model, device

    except Exception as e:
        raise ModelLoadError(f"Failed to load ESM3 model: {e}") from e


def predict_pdbs(
    model: Any,
    seq_records: Iterable,
    out_dir: Path,
    num_steps: int = 8,
    show_progress: bool = True,
    skip_existing: bool = True,
    cache_predictions: bool = False,
    cache_dir: Optional[Path] = None
) -> None:
    """
    Predict protein structures using ESM3 model.

    Args:
        model: ESM3 model instance
        seq_records: Iterable of SeqRecord objects
        out_dir: Output directory for PDB files
        num_steps: Number of generation steps
        show_progress: Show progress bar
        skip_existing: Skip sequences with existing PDB files
        cache_predictions: Cache predictions to avoid recomputation
        cache_dir: Directory for prediction cache

    Raises:
        PredictionError: If prediction fails
    """
    from esm.sdk.api import ESMProtein, GenerationConfig

    out_dir.mkdir(parents=True, exist_ok=True)

    if cache_predictions and cache_dir is None:
        cache_dir = out_dir / '.cache'
        cache_dir.mkdir(exist_ok=True)

    records = list(seq_records)
    logger.info(f"Predicting structures for {len(records)} sequences")

    iterator = tqdm(records, desc="Predicting structures") if show_progress else records

    success_count = 0
    skip_count = 0
    error_count = 0

    for rec in iterator:
        try:
            seq = str(rec.seq)
            name = rec.id.replace('|', '_').replace('/', '_').replace('\\', '_')[:80]
            outp = out_dir / f'{name}.pdb'

            # Skip if already exists
            if skip_existing and outp.exists():
                logger.debug(f"Skipping {name} (already exists)")
                skip_count += 1
                continue

            # Check cache
            if cache_predictions:
                cache_key = hashlib.md5(seq.encode()).hexdigest()
                cache_file = cache_dir / f'{cache_key}.pkl'

                if cache_file.exists():
                    logger.debug(f"Loading cached prediction for {name}")
                    with open(cache_file, 'rb') as f:
                        prot = pickle.load(f)
                else:
                    prot = ESMProtein(sequence=seq)
                    prot = model.generate(prot, GenerationConfig(track='structure', num_steps=num_steps))

                    # Save to cache
                    with open(cache_file, 'wb') as f:
                        pickle.dump(prot, f)
            else:
                prot = ESMProtein(sequence=seq)
                prot = model.generate(prot, GenerationConfig(track='structure', num_steps=num_steps))

            # Write PDB
            prot.to_pdb(str(outp))
            logger.debug(f"Predicted structure for {name}")
            success_count += 1

        except Exception as e:
            logger.error(f"Failed to predict structure for {rec.id}: {e}")
            error_count += 1
            continue

    logger.info(f"Prediction complete: {success_count} success, {skip_count} skipped, {error_count} errors")


def clear_model_cache():
    """Clear the cached ESM3 model from memory."""
    global _model_cache
    _model_cache = None
    logger.info("Model cache cleared")

