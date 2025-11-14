# ProtFlow

A modular pipeline for protein structure prediction, pocket detection, and ligand docking.

**📖 [中文文档](README_zh.md) | [Complete Documentation](DOCUMENTATION.md) | [完整文档](DOCUMENTATION_zh.md)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)

---

## Overview

ProtFlow integrates multiple bioinformatics tools into a seamless, modular pipeline:

- **GenBank Parsing** → Extract protein sequences from GenBank files
- **Structure Prediction** → Predict 3D structures with ESM3-sm
- **Pocket Detection** → Identify binding pockets with P2Rank
- **Ligand Docking** → Dock ligands with AutoDock Vina
- **Report Generation** → Create comprehensive PDF reports

**For antiSMASH BGC annotation**, use the separate [AntiSMASH_Colab.ipynb](AntiSMASH_Colab.ipynb) notebook.

**For Prokka → ESM3 → DALI workflow**, use the [Prokka_ESM3_Workflow.ipynb](Prokka_ESM3_Workflow.ipynb) notebook - a streamlined pipeline for genomic annotation and structure prediction.

Each step is independent and can be run separately or as a complete pipeline.

---

## Available Workflows

### 1. **ProtFlow** (Main Pipeline)
- **Flow**: GenBank → ESM3 → P2Rank → AutoDock Vina
- **Use**: Known protein sequences, drug discovery

### 2. **AntiSMASH Analysis**
- **Flow**: Genome → antiSMASH → BGC analysis
- **Use**: Secondary metabolite discovery

### 3. **Prokka-ESM3-DALI** ⭐
- **Flow**: FNA → Prokka → ESM3 → DALI-ready PDBs
- **Use**: Bacterial/archaeal genome annotation and structural proteomics
- **Notebook**: [Prokka_ESM3_Workflow.ipynb](Prokka_ESM3_Workflow.ipynb)

---

## Requirements

- **Python 3.12+** (recommended)
- GPU with CUDA support (recommended for structure prediction)
- HuggingFace account and token for ESM3 model access

---

## Quick Start

### Option 1: Google Colab (Recommended for Beginners)

**No installation required! Run in your browser with free GPU.**

1. Choose your workflow:
   - [ProtFlow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb) - Structure prediction & docking
   - [AntiSMASH_Colab.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/AntiSMASH_Colab.ipynb) - BGC analysis
   - [Prokka_ESM3_Workflow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/Prokka_ESM3_Workflow.ipynb) - Prokka→ESM3→DALI ⭐
2. Enable GPU: `Runtime → Change runtime type → GPU`
3. Run cells in order
4. Get HuggingFace token for ESM3 workflows: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Option 2: Local Installation

```bash
# Clone repository
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# Create virtual environment (Python 3.12+ recommended)
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install system tools (macOS)
bash scripts/setup_macos.sh
# Or for Ubuntu/Debian
bash scripts/setup_ubuntu.sh

# Verify installation
python scripts/check_deps.py
```

### Basic Usage

```bash
# Full pipeline example
python -m scripts.runner \
    --parse-gbk \
    --predict \
    --p2rank \
    --vina \
    --report \
    --smiles "CCO" \
    --limit 5
```

### CLI Options

All flags are optional - run only the steps you need:

- `--parse-gbk` - Parse GenBank files to extract proteins
- `--predict` - Predict structures with ESM3-sm
- `--p2rank` - Detect binding pockets
- `--vina` - Run molecular docking
- `--report` - Generate PDF report

**Common Parameters:**
- `--gbk-dir DIR` - GenBank files directory (default: `./esm3_pipeline/gbk_input`)
- `--smiles STR` - SMILES string for ligand
- `--ligand FILE` - Ligand file (MOL2, SDF, PDB, etc.)
- `--limit N` - Limit number of sequences
- `--config FILE` - Load configuration from file
- `--parallel` - Enable parallel processing
- `--workers N` - Number of parallel workers

---

## Requirements

- **Python**: 3.12+
- **System Tools**: Java, OpenBabel, AutoDock Vina
- **HuggingFace Token**: Required for ESM3 model access

**Set your token:**
```bash
export HF_TOKEN=hf_your_token_here
# Or login interactively
huggingface-cli login
```

---

## Examples

### Example 1: Structure Prediction Only
```bash
python -m scripts.runner --parse-gbk --predict --limit 10
```

### Example 2: Docking with SMILES
```bash
python -m scripts.runner --vina --smiles "CC(=O)O" --parallel --workers 4
```

### Example 3: Using Configuration File
Create `config.json`:
```json
{
  "max_sequences": 10,
  "enable_cache": true,
  "vina_exhaustiveness": 8
}
```

Run:
```bash
python -m scripts.runner --config config.json --predict --report
```

### Example 4: Programmatic Usage
```python
from pathlib import Path
from esm3_pipeline import seq_parser, esm3_predict

# Parse GenBank files
n = seq_parser.extract_proteins_from_gbk(
    Path("./gbk_input"),
    Path("./proteins.faa")
)

# Predict structures
model, device = esm3_predict.load_esm3_small()
selected = seq_parser.filter_and_select(Path("./proteins.faa"), limit=5)
esm3_predict.predict_pdbs(model, selected, Path("./pdbs"))
```

---

## Optional: antiSMASH

antiSMASH is not included in `requirements.txt`. Install separately:

**Bioconda (recommended):**
```bash
conda create -y -n antismash antismash
conda activate antismash
download-antismash-databases
```

**Docker (for Apple Silicon):**
```bash
mkdir -p ~/bin
curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
chmod a+x ~/bin/run_antismash
```

**Usage:**
```bash
conda activate antismash
python -m scripts.runner --antismash --gbk-dir ./esm3_pipeline/gbk_input
```

---

## Documentation

- **[README_zh.md](README_zh.md)** - Chinese brief documentation
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete English documentation with API reference
- **[DOCUMENTATION_zh.md](DOCUMENTATION_zh.md)** - Complete Chinese documentation with API reference

---

## Features

✅ **Modular Design** - Run any step independently  
✅ **High Performance** - GPU acceleration, caching, parallel processing  
✅ **Flexible Input** - GenBank, FASTA, SMILES, molecular files  
✅ **Production Ready** - Structured logging, error handling, testing  
✅ **Well Documented** - Comprehensive API docs and examples

---

## Troubleshooting

**Common issues:**
- "Java not found" → Install Java: `brew install openjdk` (macOS) or `apt-get install default-jre` (Ubuntu)
- "OpenBabel not found" → Install: `brew install open-babel` (macOS) or `apt-get install openbabel` (Ubuntu)
- "Vina not found" → Install: `brew install autodock-vina` (macOS) or `apt-get install autodock-vina` (Ubuntu)
- ESM3 model fails → Set `HF_TOKEN` environment variable

**Debug mode:**
```bash
python -m scripts.runner --log-level DEBUG --log-file debug.log --predict
```

**Check dependencies:**
```bash
python scripts/check_deps.py
```

---

## License

This repository depends on third-party tools with their own licenses (P2Rank: Apache 2.0, AutoDock Vina: Apache 2.0, OpenBabel: GPL v2, antiSMASH: AGPL v3). Review their licenses before redistribution.

---

## Citation

If you use ProtFlow in your research, please cite the underlying tools:
- **ESM**: [Evolutionary Scale Modeling](https://github.com/evolutionaryscale/esm)
- **P2Rank**: Krivák & Hoksza (2018). Journal of Cheminformatics, 10(1), 39.
- **AutoDock Vina**: Trott & Olson (2010). Journal of Computational Chemistry, 31(2), 455-461.
- **antiSMASH**: Blin et al. (2023). Nucleic Acids Research, 51(W1), W46-W50.

---

**For detailed documentation, see [DOCUMENTATION.md](DOCUMENTATION.md)**

