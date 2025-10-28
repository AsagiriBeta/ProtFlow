"""
Configuration management for ProtFlow pipeline.
Supports environment variables, config files, and defaults.
"""
from pathlib import Path
from typing import Optional, Dict, Any
import os
import json
from dataclasses import dataclass, asdict


@dataclass
class ProtFlowConfig:
    """Central configuration for the ProtFlow pipeline."""

    # Directories
    base_dir: Path = Path.cwd() / 'esm3_pipeline'
    gbk_dir: Optional[Path] = None
    pdb_dir: Optional[Path] = None
    data_dir: Optional[Path] = None
    output_dir: Optional[Path] = None

    # ESM3 model settings
    esm3_model: str = 'esm3-sm-open-v1'
    esm3_device: Optional[str] = None  # auto-detect if None
    esm3_num_steps: int = 8

    # Sequence filtering
    min_seq_length: int = 50
    max_seq_length: int = 1200
    max_sequences: int = 10

    # P2Rank settings
    p2rank_version: str = '2.5.1'
    p2rank_threads: int = 2
    p2rank_visualizations: int = 0

    # Vina settings
    vina_box_size: int = 20
    vina_exhaustiveness: int = 8
    vina_num_modes: int = 9

    # antiSMASH settings
    antismash_env: str = 'antismash'
    antismash_taxon: str = 'bacteria'

    # Logging
    log_level: str = 'INFO'
    log_file: Optional[Path] = None

    # Performance
    enable_cache: bool = True
    parallel_predictions: bool = False
    max_workers: int = 4

    # HuggingFace
    hf_token: Optional[str] = None

    def __post_init__(self):
        """Initialize derived paths and load from environment."""
        if isinstance(self.base_dir, str):
            self.base_dir = Path(self.base_dir)

        # Set derived paths if not specified
        if self.gbk_dir is None:
            self.gbk_dir = self.base_dir / 'gbk_input'
        if self.pdb_dir is None:
            self.pdb_dir = self.base_dir / 'pdbs'
        if self.data_dir is None:
            self.data_dir = self.base_dir / 'data'
        if self.output_dir is None:
            self.output_dir = self.base_dir / 'outputs'

        # Convert string paths to Path objects
        for field in ['gbk_dir', 'pdb_dir', 'data_dir', 'output_dir', 'log_file']:
            value = getattr(self, field)
            if value is not None and isinstance(value, str):
                setattr(self, field, Path(value))

        # Load from environment variables
        self._load_from_env()

        # Create directories
        self._ensure_directories()

    def _load_from_env(self):
        """Load configuration from environment variables."""
        if 'HF_TOKEN' in os.environ:
            self.hf_token = os.environ['HF_TOKEN']
        if 'ANTISMASH_ENV' in os.environ:
            self.antismash_env = os.environ['ANTISMASH_ENV']
        if 'LOG_LEVEL' in os.environ:
            self.log_level = os.environ['LOG_LEVEL']

    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_path in [self.base_dir, self.gbk_dir, self.pdb_dir,
                        self.data_dir, self.output_dir]:
            if dir_path is not None:
                dir_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_file(cls, config_path: Path) -> 'ProtFlowConfig':
        """Load configuration from a JSON or YAML file."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if config_path.suffix == '.json':
            with open(config_path) as f:
                data = json.load(f)
        elif config_path.suffix in ['.yaml', '.yml']:
            try:
                import yaml
                with open(config_path) as f:
                    data = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required to load YAML configs. Install with: pip install pyyaml")
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

        return cls(**data)

    def to_file(self, config_path: Path):
        """Save configuration to a JSON or YAML file."""
        config_path = Path(config_path)
        data = asdict(self)

        # Convert Path objects to strings for serialization
        for key, value in data.items():
            if isinstance(value, Path):
                data[key] = str(value)

        if config_path.suffix == '.json':
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif config_path.suffix in ['.yaml', '.yml']:
            try:
                import yaml
                with open(config_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            except ImportError:
                raise ImportError("PyYAML is required to save YAML configs. Install with: pip install pyyaml")
        else:
            raise ValueError(f"Unsupported config file format: {config_path.suffix}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)


# Global config instance
_config: Optional[ProtFlowConfig] = None


def get_config() -> ProtFlowConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ProtFlowConfig()
    return _config


def set_config(config: ProtFlowConfig):
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config():
    """Reset configuration to defaults."""
    global _config
    _config = ProtFlowConfig()

