# ProtFlow - Complete Documentation

**Version:** 0.2.0  
**Date:** October 28, 2025

A modular pipeline for protein structure prediction, pocket detection, and ligand docking.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Pipeline Components](#pipeline-components)
6. [API Reference](#api-reference)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [Changelog](#changelog)

---

## Overview

ProtFlow is a comprehensive toolkit that integrates multiple bioinformatics tools into seamless pipelines:

### Main Pipeline (ProtFlow)
- **GenBank Parsing**: Extract protein sequences from GenBank files
- **Structure Prediction**: Predict 3D structures using ESM3-sm model
- **Pocket Detection**: Identify binding pockets with P2Rank
- **Ligand Preparation**: Convert SMILES or molecular files to docking-ready formats
- **Molecular Docking**: Perform docking with AutoDock Vina
- **Report Generation**: Create comprehensive PDF reports

### Additional Workflows
- **AntiSMASH**: BGC annotation pipeline ([AntiSMASH_Colab.ipynb](AntiSMASH_Colab.ipynb))
- **Prokka-ESM3-DALI**: Genome annotation → structure prediction → DALI format ([Prokka_ESM3_Workflow.ipynb](Prokka_ESM3_Workflow.ipynb))

### Key Features

- **Modular Design**: Each step can be run independently
- **Flexible Input**: Support for GenBank files, FASTA sequences, SMILES, and various molecular formats
- **High Performance**: Model caching, parallel processing, and GPU acceleration
- **User-Friendly**: CLI interface, configuration files, and programmatic API
- **Well-Documented**: Comprehensive API documentation and examples
- **Production-Ready**: Structured logging, error handling, and testing

---

## Installation

### System Requirements

- **Python**: 3.12+ (recommended)

- **Python**: 3.12+
- **Operating System**: macOS, Linux, or Windows (with WSL)
- **Memory**: 8 GB RAM minimum (16+ GB recommended for structure prediction)
- **GPU**: Optional but recommended for faster ESM3 predictions

### Prerequisites

Install system dependencies:

#### macOS
```bash
bash scripts/setup_macos.sh
```

This installs:
- Java JRE (for P2Rank)
- OpenBabel (for ligand preparation)
- AutoDock Vina (for docking)

#### Ubuntu/Debian
```bash
bash scripts/setup_ubuntu.sh
```

### Python Package Installation

1. **Clone the repository**:
```bash
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow
```

2. **Create virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -U pip
pip install -r requirements.txt
```

4. **Install PyTorch** (platform-specific):

   - **macOS (Apple Silicon)**:
     ```bash
     pip install torch
     ```

   - **Linux (CPU only)**:
     ```bash
     pip install torch==2.4.* --index-url https://download.pytorch.org/whl/cpu
     ```

   - **Linux (CUDA 12.1)**:
     ```bash
     pip install torch==2.4.* --index-url https://download.pytorch.org/whl/cu121
     ```

5. **Install ProtFlow package** (development mode):
```bash
pip install -e .
```

### Verify Installation

```bash
python scripts/check_deps.py
```

You should see ✓ marks for all required dependencies.

### Hugging Face Token

ESM3 model access requires a Hugging Face token:

1. Create an account at [huggingface.co](https://huggingface.co)
2. Request access to `esm3-sm-open-v1` model
3. Create a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Set the token:
   ```bash
   export HF_TOKEN=hf_your_token_here
   # Or use interactive login
   huggingface-cli login
   ```


---

## Quick Start

### Example 1: Basic Structure Prediction

```bash
# Put your .gbk files in esm3_pipeline/gbk_input/
python -m scripts.runner --parse-gbk --predict --limit 5
```

**Output**: PDB files in `esm3_pipeline/pdbs/`

### Example 2: Full Pipeline

```bash
python -m scripts.runner \
    --parse-gbk \
    --predict \
    --p2rank \
    --vina \
    --report \
    --smiles "CCO" \
    --limit 3
```

**Output**: 
- PDB structures in `esm3_pipeline/pdbs/`
- Pocket predictions in `esm3_pipeline/pockets_summary.csv`
- Docking results in `esm3_pipeline/vina_results.csv`
- PDF report as `esm3_pipeline/esm3_results_report.pdf`

### Example 3: Using Configuration File

Create `my_config.json`:
```json
{
  "max_sequences": 10,
  "min_seq_length": 50,
  "max_seq_length": 1200,
  "enable_cache": true,
  "vina_exhaustiveness": 8,
  "num_workers": 4
}
```

Run:
```bash
python -m scripts.runner --config my_config.json --predict --report
```

### Example 4: Programmatic Usage

```python
from pathlib import Path
from esm3_pipeline.config import ProtFlowConfig
from esm3_pipeline.logger import setup_logging
from esm3_pipeline import seq_parser, esm3_predict

# Setup
logger = setup_logging(level='INFO')
config = ProtFlowConfig()

# Parse GenBank files
n = seq_parser.extract_proteins_from_gbk(
    Path("./esm3_pipeline/gbk_input"),
    Path("./proteins.faa")
)
print(f"Extracted {n} proteins")

# Filter sequences
selected = seq_parser.filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=5
)

# Predict structures
model, device = esm3_predict.load_esm3_small()
esm3_predict.predict_pdbs(model, selected, Path("./pdbs"))
```

### Prokka-ESM3-DALI Workflow

For genomic annotation and structure prediction:

```python
# Open Prokka_ESM3_Workflow.ipynb in Google Colab or Jupyter
# 1. Upload FNA file (nucleotide sequences)
# 2. Configure parameters:
OUTPUT_PREFIX = "my_genome"
KINGDOM = "Bacteria"  # or "Archaea", "Viruses"
NUM_STEPS = 8         # ESM3 generation steps
MAX_SEQ_LENGTH = 400  # Maximum protein length

# 3. Run all cells - the workflow will:
#    - Annotate genes with Prokka
#    - Predict structures with ESM3
#    - Prepare DALI-ready PDB files
#    - Package results for download
```

**Output**: ZIP file containing Prokka annotations, ESM3 structures, and DALI-ready PDB files.

---

## Configuration

### Configuration File Format

ProtFlow supports JSON and YAML configuration files.

**Example `config.json`**:
```json
{
  "base_dir": "./esm3_pipeline",
  "gbk_dir": "./esm3_pipeline/gbk_input",
  "pdb_dir": "./esm3_pipeline/pdbs",
  "esm3_model": "esm3-sm-open-v1",
  "min_seq_length": 50,
  "max_seq_length": 1200,
  "max_sequences": null,
  "enable_cache": true,
  "cache_dir": "./esm3_pipeline/.cache",
  "p2rank_version": "2.5.1",
  "vina_exhaustiveness": 8,
  "vina_box_size": 20,
  "num_workers": 4,
  "log_level": "INFO"
}
```

### Environment Variables

Configuration values can be overridden with environment variables:

```bash
export PROTFLOW_BASE_DIR="./my_output"
export PROTFLOW_MAX_SEQUENCES=20
export PROTFLOW_LOG_LEVEL="DEBUG"
export HF_TOKEN="hf_xxxxx"
```

### CLI Options

```bash
python -m scripts.runner --help
```

**Common Options**:
- `--config FILE`: Load configuration from file
- `--parse-gbk`: Parse GenBank files
- `--predict`: Run structure prediction
- `--p2rank`: Run pocket detection
- `--vina`: Run molecular docking
- `--report`: Generate PDF report
- `--gbk-dir DIR`: GenBank files directory
- `--smiles STR`: SMILES string for ligand
- `--ligand FILE`: Ligand file (MOL2, SDF, PDB, etc.)
- `--limit N`: Limit number of sequences
- `--parallel`: Enable parallel processing
- `--workers N`: Number of parallel workers
- `--log-level LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file FILE`: Log to file

---

## Pipeline Components

### 1. GenBank Parsing

Extract protein sequences from GenBank/GBFF files.

**Module**: `esm3_pipeline.seq_parser`

**Features**:
- Recursive directory search
- CDS translation extraction
- Metadata preservation (locus_tag, product, gene)
- Sequence deduplication
- Length filtering
- Sorting by length

**Usage**:
```python
from esm3_pipeline.seq_parser import extract_proteins_from_gbk

count = extract_proteins_from_gbk(
    gbk_dir=Path("./gbk_input"),
    out_fasta=Path("./proteins.faa"),
    recursive=True,
    deduplicate=True
)
```

### 2. Structure Prediction (ESM3)

Predict 3D protein structures using the ESM3-sm model.

**Module**: `esm3_pipeline.esm3_predict`

**Features**:
- GPU/MPS/CPU auto-detection
- Model caching
- Prediction caching
- Progress tracking
- Batch processing
- Skip existing files

**Usage**:
```python
from esm3_pipeline.esm3_predict import load_esm3_small, predict_pdbs
from Bio import SeqIO

model, device = load_esm3_small()
sequences = list(SeqIO.parse("proteins.faa", "fasta"))

predict_pdbs(
    model=model,
    seq_records=sequences,
    out_dir=Path("./pdbs"),
    num_steps=8,
    show_progress=True,
    cache_predictions=True
)
```

### 3. Pocket Detection (P2Rank)

Identify and score potential binding pockets.

**Module**: `esm3_pipeline.p2rank`

**Features**:
- Automatic P2Rank download
- Multi-threaded execution
- Pocket ranking by score
- Coordinate extraction
- CSV output

**Usage**:
```python
from esm3_pipeline.p2rank import ensure_p2rank, run_p2rank_on_pdbs

p2rank_jar = ensure_p2rank(version="2.5.1")
results = run_p2rank_on_pdbs(
    p2rank_jar=p2rank_jar,
    pdb_dir=Path("./pdbs"),
    threads=2,
    top_n_pockets=1
)
```

### 4. Ligand Preparation

Convert ligands to PDBQT format for docking.

**Module**: `esm3_pipeline.ligand_prep`

**Features**:
- SMILES to 3D structure
- Support for MOL2, SDF, MOL, PDB formats
- pH-dependent protonation
- PDBQT conversion with OpenBabel
- Automatic charge calculation

**Usage**:
```python
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt

# From SMILES
pdbqt = smiles_or_file_to_pdbqt(
    input_str="CCO",
    output_name="ethanol",
    ph=7.4
)

# From file
pdbqt = smiles_or_file_to_pdbqt(
    input_str="ligand.mol2"
)
```

### 5. Molecular Docking (AutoDock Vina)

Perform protein-ligand docking.

**Module**: `esm3_pipeline.vina_dock`

**Features**:
- Automatic receptor PDBQT preparation
- Parallel docking support
- Multiple binding modes
- Configurable search space
- Energy scoring

**Usage**:
```python
from esm3_pipeline.vina_dock import run_vina
import pandas as pd

pockets_df = pd.read_csv("pockets.csv")

results = run_vina(
    ligand_pdbqt=Path("ligand.pdbqt"),
    pockets=pockets_df,
    box_size=20,
    exhaustiveness=8,
    num_modes=9,
    parallel=True,
    max_workers=4
)
```

### 6. Report Generation

Create comprehensive PDF reports.

**Module**: `esm3_pipeline.reporting`

**Features**:
- Summary statistics
- Structure visualizations
- Docking results tables
- Pocket information
- Customizable layout

**Usage**:
```python
from esm3_pipeline.reporting import build_report

build_report(
    base=Path("./"),
    pdb_dir=Path("./pdbs"),
    out_pdf=Path("./report.pdf")
)
```

**Note**: For antiSMASH BGC annotation, use the separate [AntiSMASH_Colab.ipynb](AntiSMASH_Colab.ipynb) notebook.

---

## API Reference

### Configuration (`esm3_pipeline.config`)

#### `ProtFlowConfig`

Central configuration class.

```python
from esm3_pipeline.config import ProtFlowConfig

# Default config
config = ProtFlowConfig()

# Load from file
config = ProtFlowConfig.from_file("config.json")

# Save to file
config.to_file("config.json")

# Access values
print(config.base_dir)
print(config.esm3_model)
```

**Attributes**:
- `base_dir`: Base output directory
- `gbk_dir`: GenBank files directory
- `pdb_dir`: PDB files directory
- `esm3_model`: ESM3 model name
- `min_seq_length`: Minimum sequence length
- `max_seq_length`: Maximum sequence length
- `max_sequences`: Maximum number of sequences (None = unlimited)
- `enable_cache`: Enable caching
- `cache_dir`: Cache directory
- `p2rank_version`: P2Rank version
- `vina_exhaustiveness`: Vina search exhaustiveness
- `vina_box_size`: Docking box size (Å)
- `num_workers`: Number of parallel workers
- `log_level`: Logging level

### Sequence Parser (`esm3_pipeline.seq_parser`)

#### `extract_proteins_from_gbk()`

Extract proteins from GenBank files.

```python
from esm3_pipeline.seq_parser import extract_proteins_from_gbk
from pathlib import Path

count = extract_proteins_from_gbk(
    gbk_dir: Path,
    out_fasta: Path,
    recursive: bool = True,
    deduplicate: bool = True
) -> int
```

**Parameters**:
- `gbk_dir`: Directory containing .gbk/.gbff files
- `out_fasta`: Output FASTA file path
- `recursive`: Search subdirectories
- `deduplicate`: Remove duplicate sequences

**Returns**: Number of sequences written

#### `filter_and_select()`

Filter and select sequences.

```python
from esm3_pipeline.seq_parser import filter_and_select

selected = filter_and_select(
    fasta: Path,
    min_len: int = 50,
    max_len: int = 1200,
    limit: Optional[int] = None,
    out_fasta: Optional[Path] = None,
    sort_by_length: bool = False
) -> List[SeqRecord]
```

**Parameters**:
- `fasta`: Input FASTA file
- `min_len`: Minimum sequence length
- `max_len`: Maximum sequence length
- `limit`: Maximum number of sequences to return
- `out_fasta`: Optional output file
- `sort_by_length`: Sort sequences by length

**Returns**: List of SeqRecord objects

### ESM3 Prediction (`esm3_pipeline.esm3_predict`)

#### `load_esm3_small()`

Load ESM3 model.

```python
from esm3_pipeline.esm3_predict import load_esm3_small

model, device = load_esm3_small(
    device: Optional[str] = None,
    model_name: str = 'esm3-sm-open-v1',
    use_cache: bool = True
) -> Tuple[Any, str]
```

**Parameters**:
- `device`: Device to use ('cuda', 'mps', 'cpu', or None for auto)
- `model_name`: ESM3 model name
- `use_cache`: Use cached model if available

**Returns**: Tuple of (model, device)

#### `predict_pdbs()`

Predict protein structures.

```python
from esm3_pipeline.esm3_predict import predict_pdbs

predict_pdbs(
    model: Any,
    seq_records: List[SeqRecord],
    out_dir: Path,
    num_steps: int = 8,
    show_progress: bool = True,
    skip_existing: bool = True,
    cache_predictions: bool = True
) -> None
```

**Parameters**:
- `model`: Loaded ESM3 model
- `seq_records`: List of sequences to predict
- `out_dir`: Output directory for PDB files
- `num_steps`: Number of prediction steps
- `show_progress`: Show progress bar
- `skip_existing`: Skip if PDB already exists
- `cache_predictions`: Cache predictions

### P2Rank (`esm3_pipeline.p2rank`)

#### `ensure_p2rank()`

Download and setup P2Rank.

```python
from esm3_pipeline.p2rank import ensure_p2rank

p2rank_jar = ensure_p2rank(
    base_dir: Path = Path("."),
    version: str = "2.5.1",
    force_download: bool = False
) -> Path
```

**Parameters**:
- `base_dir`: Base directory for downloads
- `version`: P2Rank version
- `force_download`: Force re-download

**Returns**: Path to P2Rank JAR file

#### `run_p2rank_on_pdbs()`

Run P2Rank on PDB files.

```python
from esm3_pipeline.p2rank import run_p2rank_on_pdbs

results = run_p2rank_on_pdbs(
    p2rank_jar: Path,
    pdb_dir: Path,
    threads: int = 2,
    visualizations: int = 0,
    top_n_pockets: int = 1
) -> List[Dict[str, Any]]
```

**Parameters**:
- `p2rank_jar`: Path to P2Rank JAR
- `pdb_dir`: Directory with PDB files
- `threads`: Number of threads
- `visualizations`: Visualization level (0-3)
- `top_n_pockets`: Number of top pockets to return per protein

**Returns**: List of pocket dictionaries

### Ligand Preparation (`esm3_pipeline.ligand_prep`)

#### `smiles_or_file_to_pdbqt()`

Convert ligand to PDBQT format.

```python
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt

pdbqt_path = smiles_or_file_to_pdbqt(
    input_str: str,
    base_dir: Path = Path("."),
    output_name: str = "ligand",
    ph: float = 7.4
) -> Path
```

**Parameters**:
- `input_str`: SMILES string or path to ligand file
- `base_dir`: Base directory for outputs
- `output_name`: Output file base name
- `ph`: pH for protonation

**Returns**: Path to PDBQT file

### Vina Docking (`esm3_pipeline.vina_dock`)

#### `run_vina()`

Run AutoDock Vina docking.

```python
from esm3_pipeline.vina_dock import run_vina
import pandas as pd

results_df = run_vina(
    ligand_pdbqt: Path,
    pockets: pd.DataFrame,
    out_base: Path = Path("."),
    box_size: float = 20.0,
    exhaustiveness: int = 8,
    num_modes: int = 9,
    parallel: bool = False,
    max_workers: int = 4
) -> pd.DataFrame
```

**Parameters**:
- `ligand_pdbqt`: Path to ligand PDBQT file
- `pockets`: DataFrame with pocket information
- `out_base`: Base directory for outputs
- `box_size`: Search box size (Å)
- `exhaustiveness`: Search exhaustiveness
- `num_modes`: Number of binding modes
- `parallel`: Enable parallel processing
- `max_workers`: Number of parallel workers

**Returns**: DataFrame with docking results

### Logging (`esm3_pipeline.logger`)

#### `setup_logging()`

Configure logging system.

```python
from esm3_pipeline.logger import setup_logging

logger = setup_logging(
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger
```

**Parameters**:
- `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: Optional log file path
- `console`: Enable console output

**Returns**: Configured logger

#### `get_logger()`

Get module logger.

```python
from esm3_pipeline.logger import get_logger

logger = get_logger(__name__)
logger.info("Processing started")
logger.debug("Debug information")
logger.error("Error occurred")
```

### Exceptions

Custom exception hierarchy for better error handling.

```python
from esm3_pipeline.exceptions import (
    ProtFlowError,           # Base exception
    ConfigurationError,      # Configuration errors
    DependencyError,         # Missing dependencies
    ModelLoadError,          # Model loading failures
    PredictionError,         # Prediction failures
    PocketDetectionError,    # P2Rank failures
    DockingError,           # Vina failures
    LigandPreparationError, # Ligand prep failures
    ParseError,             # GenBank parsing failures
    AntiSMASHError          # antiSMASH failures
)
```

---

## Advanced Usage

### Complete Workflow Example

```python
from pathlib import Path
from esm3_pipeline.config import ProtFlowConfig, set_config
from esm3_pipeline.logger import setup_logging
from esm3_pipeline.seq_parser import extract_proteins_from_gbk, filter_and_select
from esm3_pipeline.esm3_predict import load_esm3_small, predict_pdbs
from esm3_pipeline.p2rank import ensure_p2rank, run_p2rank_on_pdbs
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt
from esm3_pipeline.vina_dock import run_vina
from esm3_pipeline.reporting import build_report
import pandas as pd

# Setup
logger = setup_logging(level='INFO', log_file=Path("pipeline.log"))
config = ProtFlowConfig()
set_config(config)

# 1. Parse GenBank files
logger.info("Step 1: Parsing GenBank files")
n = extract_proteins_from_gbk(
    Path("./gbk_input"),
    Path("./proteins.faa")
)
logger.info(f"Extracted {n} proteins")

# 2. Filter and select sequences
logger.info("Step 2: Filtering sequences")
selected = filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=10,
    out_fasta=Path("./selected.faa")
)
logger.info(f"Selected {len(selected)} sequences")

# 3. Predict structures
logger.info("Step 3: Predicting structures")
model, device = load_esm3_small()
predict_pdbs(model, selected, Path("./pdbs"))

# 4. Detect pockets
logger.info("Step 4: Detecting pockets")
p2jar = ensure_p2rank(Path("./"))
pockets = run_p2rank_on_pdbs(p2jar, Path("./pdbs"))
pockets_df = pd.DataFrame(pockets)
pockets_df.to_csv("pockets.csv", index=False)
logger.info(f"Found {len(pockets)} pockets")

# 5. Prepare ligand
logger.info("Step 5: Preparing ligand")
ligand = smiles_or_file_to_pdbqt("CCO", Path("./"))

# 6. Run docking
logger.info("Step 6: Running docking")
results = run_vina(
    ligand, 
    pockets_df, 
    Path("./docking"),
    parallel=True,
    max_workers=4
)
results.to_csv("vina_results.csv", index=False)
logger.info(f"Completed {len(results)} docking runs")

# 7. Generate report
logger.info("Step 7: Generating report")
build_report(Path("./"), Path("./pdbs"), Path("./report.pdf"))

logger.info("Pipeline complete!")
```

### Parallel Processing

Enable parallel processing for faster execution:

```bash
# Parallel docking with 8 workers
python -m scripts.runner --vina --parallel --workers 8 --smiles "CCO"
```

Programmatically:
```python
from esm3_pipeline.vina_dock import run_vina

results = run_vina(
    ligand_pdbqt,
    pockets_df,
    parallel=True,
    max_workers=8
)
```

### Caching

Enable caching to speed up re-runs:

```python
from esm3_pipeline.config import ProtFlowConfig

config = ProtFlowConfig()
config.enable_cache = True
config.cache_dir = Path("./.cache")
```

Or via config file:
```json
{
  "enable_cache": true,
  "cache_dir": "./.cache"
}
```

### Custom Workflows

Run only specific steps:

```bash
# Only parse GenBank files
python -m scripts.runner --parse-gbk

# Only run pocket detection (requires existing PDBs)
python -m scripts.runner --p2rank

# Only generate report
python -m scripts.runner --report
```

---

## Troubleshooting

### Common Issues

#### 1. "Java not found"

**Solution**: Install Java JRE
```bash
# macOS
brew install openjdk

# Ubuntu
sudo apt-get install default-jre

# Verify
java -version
```

#### 2. "OpenBabel not found"

**Solution**: Install OpenBabel
```bash
# macOS
brew install open-babel

# Ubuntu
sudo apt-get install openbabel

# Verify
obabel -V
```

#### 3. "AutoDock Vina not found"

**Solution**: Install Vina
```bash
# macOS
brew install autodock-vina

# Ubuntu
sudo apt-get install autodock-vina

# Verify
vina --version
```

#### 4. "No sequences found in GenBank files"

**Causes**:
- GenBank files are empty or corrupted
- No CDS features with translations
- Wrong directory path

**Solution**:
- Verify GenBank files contain CDS features
- Check the `--gbk-dir` path
- Try with a sample GenBank file

#### 5. ESM3 model fails to load

**Causes**:
- Missing or invalid HuggingFace token
- No access to esm3-sm-open-v1 model
- Network issues

**Solution**:
```bash
# Set token
export HF_TOKEN=hf_xxxxxxxxxxxxx

# Or login interactively
huggingface-cli login

# Verify access
python -c "from huggingface_hub import HfApi; HfApi().model_info('esm3-sm-open-v1')"
```

#### 6. Out of memory errors

**Causes**:
- Sequences too long
- Insufficient RAM/VRAM

**Solution**:
- Reduce sequence length limits:
  ```bash
  python -m scripts.runner --predict --max-len 800
  ```
- Process fewer sequences at once:
  ```bash
  python -m scripts.runner --predict --limit 5
  ```
- Use CPU instead of GPU for smaller memory footprint

#### 7. P2Rank fails silently

**Causes**:
- Invalid PDB files
- Java heap space issues
- Missing Java

**Solution**:
- Verify PDB files are valid
- Increase Java heap space:
  ```bash
  export JAVA_OPTS="-Xmx4g"
  ```
- Check Java installation:
  ```bash
  java -version
  ```

#### 8. antiSMASH: "command not found"

**Causes**:
- antiSMASH not installed
- Wrong conda environment
- PATH not set

**Solution**:
```bash
# Activate conda environment
conda activate antismash

# Verify installation
which antismash
antismash --version

# If using Docker wrapper
which run_antismash
```

#### 9. Docking produces poor results

**Possible improvements**:
- Increase exhaustiveness:
  ```bash
  python -m scripts.runner --vina --exhaustiveness 16
  ```
- Increase box size:
  ```bash
  python -m scripts.runner --vina --box-size 25
  ```
- Use more binding modes:
  ```bash
  python -m scripts.runner --vina --num-modes 20
  ```

#### 10. Slow performance

**Optimizations**:
- Enable caching:
  ```json
  {"enable_cache": true}
  ```
- Use GPU for structure prediction
- Enable parallel docking:
  ```bash
  python -m scripts.runner --vina --parallel --workers 8
  ```
- Reduce number of sequences:
  ```bash
  python -m scripts.runner --predict --limit 10
  ```

### Debug Mode

Enable detailed logging:

```bash
python -m scripts.runner --log-level DEBUG --log-file debug.log --predict
```

Check the log file for detailed information about what's happening.

### Getting Help

1. **Check documentation**: README.md, API.md, this file
2. **Run dependency check**: `python scripts/check_deps.py`
3. **Enable debug logging**: `--log-level DEBUG`
4. **Check issue tracker**: [GitHub Issues](https://github.com/AsagiriBeta/ProtFlow/issues)
5. **Ask for help**: Open a new issue with:
   - Your OS and Python version
   - Full command or script
   - Complete error message
   - Output of `python scripts/check_deps.py`

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors

1. **Fork and clone**:
```bash
git clone https://github.com/YOUR_USERNAME/ProtFlow.git
cd ProtFlow
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate
```

3. **Install in development mode**:
```bash
pip install -e ".[dev]"
```

4. **Create a branch**:
```bash
git checkout -b feature/your-feature-name
```

5. **Make changes and test**:
```bash
pytest tests/
```

6. **Check code quality**:
```bash
black esm3_pipeline scripts
isort esm3_pipeline scripts
flake8 esm3_pipeline scripts
mypy esm3_pipeline
```

7. **Commit and push**:
```bash
git add .
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

8. **Create Pull Request** on GitHub

### Code Style

- Follow PEP 8
- Use type hints
- Write comprehensive docstrings
- Add tests for new features
- Keep functions focused and modular

### Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=esm3_pipeline tests/

# Run specific test
pytest tests/test_pipeline.py::test_function_name
```

---

## Changelog

### [0.2.0] - 2025-10-28

#### Added
- **Configuration Management**: Centralized config system with JSON/YAML support
- **Logging System**: Structured logging with colored console output and file logging
- **Error Handling**: Custom exception hierarchy for better error messages
- **Testing**: Comprehensive test suite with CI/CD integration
- **Performance**: Model caching, parallel docking, prediction caching
- **Features**: Sequence deduplication, input validation, multiple pockets support
- **Development Tools**: setup.py, .gitignore, GitHub Actions, code quality tools

#### Changed
- **Refactored Modules**: All modules enhanced with type hints and docstrings
- **Improved CLI**: Better argument handling and validation
- **Enhanced Documentation**: Comprehensive API docs and examples

#### Fixed
- GenBank parsing edge cases
- Memory leaks in model loading
- Race conditions in parallel docking
- Path handling on Windows

### [0.1.0] - 2025-10-15

- Initial release
- Basic pipeline functionality
- Jupyter notebook interface

---

## License

This repository contains a workflow that depends on third-party tools with their own licenses:
- **P2Rank**: Apache License 2.0
- **AutoDock Vina**: Apache License 2.0
- **OpenBabel**: GPL v2
- **ESM3**: Model-specific license (check HuggingFace)
- **antiSMASH**: AGPL v3

Please review their licenses before redistribution.

---

## Citation

If you use ProtFlow in your research, please cite:

```bibtex
@software{protflow2025,
  title={ProtFlow: A Modular Pipeline for Protein Structure Prediction and Analysis},
  author={Your Name},
  year={2025},
  url={https://github.com/AsagiriBeta/ProtFlow}
}
```

And cite the underlying tools:
- **ESM**: [Evolutionary Scale Modeling](https://github.com/evolutionaryscale/esm)
- **P2Rank**: Krivák, R., & Hoksza, D. (2018). P2Rank: machine learning based tool for rapid and accurate prediction of ligand binding sites from protein structure. Journal of cheminformatics, 10(1), 39.
- **AutoDock Vina**: Trott, O., & Olson, A. J. (2010). AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of computational chemistry, 31(2), 455-461.
- **antiSMASH**: Blin, K., et al. (2023). antiSMASH 7.0: new and improved predictions for detection, regulation, chemical structures and visualisation. Nucleic acids research, 51(W1), W46-W50.

---

**For more information, visit the [GitHub repository](https://github.com/AsagiriBeta/ProtFlow).**

