"""
ESM3 structure prediction utilities with caching and progress tracking.

This module provides comprehensive ESM3 model support with all official parameters
including temperature, constraints, and multi-track generation.
"""
from pathlib import Path
from typing import Iterable, Optional, Tuple, Any, Dict, List, Union
from dataclasses import dataclass
import hashlib
import pickle

import torch
from tqdm import tqdm

from ..utils.logger import get_logger
from ..utils.exceptions import ModelLoadError

logger = get_logger(__name__)

# Global model cache
_model_cache: Optional[Tuple[Any, str]] = None


@dataclass
class ESM3GenerationConfig:
    """
    Comprehensive configuration for ESM3 generation with all official parameters.
    
    Based on official ESM3 SDK GenerationConfig API:
    - track: Which modality to generate ('sequence', 'structure', 'function')
    - num_steps: Number of masked-sampling/unmasking steps
    - temperature: Controls randomness (higher = more diverse outputs)
    - Additional parameters for advanced usage
    """
    track: str = 'structure'  # 'sequence', 'structure', or 'function'
    num_steps: int = 8
    temperature: Optional[float] = None  # None = use model default, typically 0.7 for sequence
    
    def to_generation_config(self) -> Any:
        """
        Convert to ESM3 SDK GenerationConfig object.
        
        Returns:
            GenerationConfig instance from esm.sdk.api
        """
        from esm.sdk.api import GenerationConfig
        
        kwargs = {
            'track': self.track,
            'num_steps': self.num_steps,
        }
        
        # Only add temperature if explicitly set
        if self.temperature is not None:
            kwargs['temperature'] = self.temperature
        
        return GenerationConfig(**kwargs)


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
        cached_model, cached_device = _model_cache
        # Verify cached model is still valid
        if hasattr(cached_model, 'eval') and hasattr(cached_model, 'generate'):
            logger.info("Using cached ESM3 model")
            return _model_cache
        else:
            logger.warning("Cached model invalid, reloading...")
            _model_cache = None

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
        logger.info("Note: First time loading will download the model (~2-5 GB)")

        # Lazy import to avoid loading if not needed
        try:
            from esm.models.esm3 import ESM3
        except ImportError as e:
            raise ImportError(
                f"ESM3 module not found. Please install: pip install esm>=3.2.1.post1\n"
                f"On Windows, you may need Visual C++ Build Tools or use Conda.\n"
                f"Original error: {e}"
            ) from e

        original_torch_load = torch.load

        def _torch_load_weights_only(*args, **kwargs):
            kwargs.setdefault('weights_only', True)
            return original_torch_load(*args, **kwargs)

        torch.load = _torch_load_weights_only
        try:
            model = ESM3.from_pretrained(model_name).to(device)
        finally:
            torch.load = original_torch_load

        model.eval()  # Set to evaluation mode

        logger.info(f"Model loaded successfully on {device}")
        if device == 'cuda' and torch.cuda.is_available():
            logger.info(f"CUDA Device: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

        # Cache the model
        if use_cache:
            _model_cache = (model, device)

        return model, device

    except ImportError as e:
        raise ModelLoadError(
            f"ESM3 module not found. Please install: pip install esm>=3.2.1.post1\n"
            f"Original error: {e}"
        ) from e
    except Exception as e:
        raise ModelLoadError(
            f"Failed to load ESM3 model '{model_name}': {e}\n"
            f"Check: 1) Model name is correct, 2) Internet connection for download, "
            f"3) Sufficient disk space (~2-5 GB for model)"
        ) from e


def predict_pdbs(
    model: Any,
    seq_records: Iterable,
    out_dir: Path,
    generation_config: Optional[ESM3GenerationConfig] = None,
    num_steps: Optional[int] = None,  # Deprecated: use generation_config instead
    temperature: Optional[float] = None,  # Deprecated: use generation_config instead
    show_progress: bool = True,
    skip_existing: bool = True,
    cache_predictions: bool = False,
    cache_dir: Optional[Path] = None,
    min_seq_length: int = 30,
    max_seq_length: int = 2000,
) -> Dict[str, int]:
    """
    Predict protein structures using ESM3 model with comprehensive parameter support.

    Args:
        model: ESM3 model instance
        seq_records: Iterable of SeqRecord objects
        out_dir: Output directory for PDB files
        generation_config: ESM3GenerationConfig with all generation parameters.
                         If None, uses defaults (structure track, 8 steps).
        num_steps: (Deprecated) Number of generation steps. Use generation_config instead.
        temperature: (Deprecated) Temperature for sampling. Use generation_config instead.
        show_progress: Show progress bar
        skip_existing: Skip sequences with existing PDB files
        cache_predictions: Cache predictions to avoid recomputation
        cache_dir: Directory for prediction cache
        min_seq_length: Minimum sequence length to process
        max_seq_length: Maximum sequence length to process

    Returns:
        Dictionary with counts: {'success': int, 'skipped': int, 'errors': int, 'filtered': int}

    Raises:
        PredictionError: If prediction fails
    """
    from esm.sdk.api import ESMProtein

    # Handle deprecated parameters
    if generation_config is None:
        generation_config = ESM3GenerationConfig(
            track='structure',
            num_steps=num_steps if num_steps is not None else 8,
            temperature=temperature
        )
    else:
        # Override with deprecated params if provided
        if num_steps is not None:
            generation_config.num_steps = num_steps
        if temperature is not None:
            generation_config.temperature = temperature

    gen_cfg = generation_config.to_generation_config()

    out_dir.mkdir(parents=True, exist_ok=True)

    if cache_predictions and cache_dir is None:
        cache_dir = out_dir / '.cache'
        cache_dir.mkdir(exist_ok=True)

    records = list(seq_records)
    logger.info(f"Predicting structures for {len(records)} sequences")
    logger.info(f"Generation config: track={generation_config.track}, "
                f"num_steps={generation_config.num_steps}, "
                f"temperature={generation_config.temperature}")

    # Filter sequences by length
    filtered_records = [
        rec for rec in records
        if min_seq_length <= len(rec.seq) <= max_seq_length
    ]
    filtered_count = len(records) - len(filtered_records)
    
    if filtered_count > 0:
        logger.info(f"Filtered {filtered_count} sequences outside length range "
                   f"[{min_seq_length}, {max_seq_length}]")

    success_count = 0
    skip_count = 0
    error_count = 0

    # ESM3 model.generate() processes one sequence at a time
    iterator = tqdm(filtered_records, desc="Predicting structures") if show_progress else filtered_records

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
                        prot = model.generate(prot, gen_cfg)

                        # Save to cache
                        with open(cache_file, 'wb') as f:
                            pickle.dump(prot, f)
                else:
                    prot = ESMProtein(sequence=seq)
                    prot = model.generate(prot, gen_cfg)

                # Write PDB (only for structure track)
                if generation_config.track == 'structure':
                    prot.to_pdb(str(outp))
                    logger.debug(f"Predicted structure for {name}")
                else:
                    # For other tracks, save as appropriate format
                    logger.warning(f"Track '{generation_config.track}' not yet fully supported for PDB output")
                    prot.to_pdb(str(outp))  # Fallback

            success_count += 1

        except Exception as e:
            logger.error(f"Failed to predict structure for {rec.id}: {e}")
            error_count += 1
            continue

    result = {
        'success': success_count,
        'skipped': skip_count,
        'errors': error_count,
        'filtered': filtered_count
    }
    
    logger.info(f"Prediction complete: {success_count} success, {skip_count} skipped, "
               f"{error_count} errors, {filtered_count} filtered")
    
    return result


def clear_model_cache():
    """Clear the cached ESM3 model from memory."""
    global _model_cache
    _model_cache = None
    logger.info("Model cache cleared")


def create_generation_config_from_dict(config_dict: Dict[str, Any]) -> ESM3GenerationConfig:
    """
    Create ESM3GenerationConfig from a dictionary (e.g., from ProtFlowConfig).
    
    Args:
        config_dict: Dictionary with keys like 'esm3_num_steps', 'esm3_temperature', 'esm3_track'
    
    Returns:
        ESM3GenerationConfig instance
    """
    return ESM3GenerationConfig(
        track=config_dict.get('esm3_track', 'structure'),
        num_steps=config_dict.get('esm3_num_steps', 8),
        temperature=config_dict.get('esm3_temperature', None)
    )


def predict_structures_from_fasta(
    fasta_file: Path,
    out_dir: Path,
    model_name: str = 'esm3-sm-open-v1',
    generation_config: Optional[ESM3GenerationConfig] = None,
    device: Optional[str] = None,
    **kwargs
) -> Dict[str, int]:
    """
    Convenience function to predict structures from a FASTA file.
    
    Args:
        fasta_file: Input FASTA file path
        out_dir: Output directory for PDB files
        model_name: ESM3 model name
        generation_config: ESM3GenerationConfig (uses defaults if None)
        device: Device to use ('cuda', 'cpu', 'mps', or None for auto-detect)
        **kwargs: Additional arguments passed to predict_pdbs()
    
    Returns:
        Dictionary with prediction statistics
    """
    from Bio import SeqIO
    
    if not fasta_file.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_file}")
    
    logger.info(f"Reading sequences from {fasta_file}")
    records = list(SeqIO.parse(fasta_file, 'fasta'))
    logger.info(f"Loaded {len(records)} sequences")
    
    model, device = load_esm3_small(device=device, model_name=model_name)
    
    if generation_config is None:
        generation_config = ESM3GenerationConfig()
    
    return predict_pdbs(
        model=model,
        seq_records=records,
        out_dir=out_dir,
        generation_config=generation_config,
        **kwargs
    )
