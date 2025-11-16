# ProtFlow

A modular pipeline for protein structure prediction, pocket detection, and ligand docking.

**📖 [中文文档](README_zh.md)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)

---

## 🚀 Available Workflows

### 1. **ProtFlow** - Structure Prediction & Docking
- **Flow**: GenBank → ESM3 → P2Rank → AutoDock Vina
- **Notebook**: [ProtFlow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)
- **Use**: Drug discovery, binding site analysis

### 2. **AntiSMASH** - BGC Analysis
- **Flow**: Genome → antiSMASH → BGC annotation
- **Notebook**: [AntiSMASH_Colab.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/AntiSMASH_Colab.ipynb)
- **Use**: Secondary metabolite discovery

### 3. **Prokka → ESM3 → DALI** ⭐
- **Flow**: FNA → Prokka → ESM3 → DALI-ready PDBs
- **Notebooks**: 
  - Colab: [Prokka_ESM3_Workflow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/Prokka_ESM3_Workflow.ipynb)
  - JupyterLab: [Prokka_ESM3_Workflow_JLab.ipynb](Prokka_ESM3_Workflow_JLab.ipynb)
- **Use**: Genome annotation, structural proteomics

---

## 📦 Quick Start

### Option 1: Google Colab (Easiest - No Installation!)

1. Click a workflow link above
2. Enable GPU: `Runtime → Change runtime type → GPU`
3. Get HuggingFace token: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. Run cells in order

### Option 2: Local / JupyterLab

```bash
# Clone repository
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set HuggingFace token
export HF_TOKEN=hf_your_token_here

# Run CLI
python -m scripts.runner --parse-gbk --predict --limit 5

# Or launch JupyterLab
jupyter lab
```

**For Prokka workflow on JupyterLab:**
```bash
# Install micromamba (if needed)
brew install micromamba  # macOS
# or: curl -Ls https://micro.mamba.pm/install.sh | bash

# Create Prokka environment
micromamba create -y -n prokka -c bioconda prokka python=3.10
micromamba run -n prokka prokka --setupdb

# Launch notebook
jupyter lab Prokka_ESM3_Workflow_JLab.ipynb
```

See `.env.example` for configuration options.

---

## 💡 Usage Examples

### CLI Pipeline
```bash
# Full pipeline: parse → predict → dock → report
python -m scripts.runner --parse-gbk --predict --p2rank --vina --report --smiles "CCO" --limit 5

# Structure prediction only
python -m scripts.runner --predict --limit 10

# Docking with custom ligand
python -m scripts.runner --vina --ligand my_drug.mol2 --parallel

# antiSMASH BGC analysis
python -m scripts.runner --antismash --gbk-dir ./genomes
```

**CLI Options:**
```bash
# Workflow steps (run any combination)
--parse-gbk          # Extract proteins from GenBank files
--predict            # Predict 3D structures with ESM3
--p2rank             # Detect binding pockets
--vina               # Run molecular docking
--report             # Generate PDF report
--antismash          # Run antiSMASH BGC analysis

# Input/Output
--gbk-dir DIR        # GenBank files directory (default: ./esm3_pipeline/gbk_input)
--smiles STR         # Ligand SMILES string
--ligand FILE        # Ligand file (MOL2/SDF/PDB/etc.)
--limit N            # Max sequences to process
--config FILE        # Load config from JSON/YAML

# Performance
--parallel           # Enable parallel processing
--workers N          # Number of parallel workers (default: 4)
--log-level LEVEL    # Logging level: DEBUG/INFO/WARNING/ERROR
```

### Python API
```python
from pathlib import Path
from esm3_pipeline import seq_parser, esm3_predict, p2rank, vina_dock

# 1. Parse GenBank files
n = seq_parser.extract_proteins_from_gbk(
    Path("./gbk_input"), 
    Path("./proteins.faa")
)

# 2. Filter and select sequences
selected = seq_parser.filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=5
)

# 3. Predict structures
model, device = esm3_predict.load_esm3_small()
esm3_predict.predict_pdbs(model, selected, Path("./pdbs"))

# 4. Detect pockets
p2rank.run_p2rank_batch(Path("./pdbs"), Path("./pockets"))

# 5. Dock ligand
from esm3_pipeline.ligand_prep import smiles_to_pdbqt
ligand = smiles_to_pdbqt("CCO", Path("./ligand.pdbqt"))
vina_dock.dock_to_pockets(
    Path("./pdbs/protein.pdb"),
    ligand,
    Path("./pockets/protein_predictions.csv"),
    Path("./docking")
)
```

### Config File
Create `config.json`:
```json
{
  "max_sequences": 10,
  "min_seq_length": 50,
  "max_seq_length": 1200,
  "enable_cache": true,
  "vina_exhaustiveness": 8,
  "vina_box_size": 20,
  "num_workers": 4,
  "log_level": "INFO"
}
```
Run: `python -m scripts.runner --config config.json --predict --report`

### Environment Variables
```bash
export HF_TOKEN=hf_xxxxx              # HuggingFace token (required)
export PROTFLOW_BASE_DIR=./output     # Base directory
export PROTFLOW_MAX_SEQUENCES=20      # Max sequences
export PROTFLOW_LOG_LEVEL=DEBUG       # Log level
```

---

## 🔧 Optional: antiSMASH

antiSMASH is not in `requirements.txt`. Install separately:

```bash
# Bioconda (recommended)
conda create -y -n antismash antismash
conda activate antismash
download-antismash-databases

# Docker (Apple Silicon)
mkdir -p ~/bin
curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
chmod a+x ~/bin/run_antismash
```

---

## 📚 Features

✅ **Modular Design** - Run any step independently  
✅ **High Performance** - GPU acceleration, caching, parallel processing  
✅ **Flexible Input** - GenBank, FASTA, SMILES, molecular files  
✅ **Production Ready** - Structured logging, error handling, testing  
✅ **Well Documented** - Comprehensive guides and examples

### Project Structure
```
ProtFlow/
├── esm3_pipeline/          # Core modules
│   ├── seq_parser.py       # GenBank/FASTA parsing
│   ├── esm3_predict.py     # ESM3 structure prediction
│   ├── p2rank.py           # P2Rank pocket detection
│   ├── ligand_prep.py      # Ligand preparation (SMILES/files)
│   ├── vina_dock.py        # AutoDock Vina docking
│   ├── reporting.py        # PDF report generation
│   └── config.py           # Configuration management
├── scripts/
│   ├── runner.py           # Main CLI entry point
│   ├── check_deps.py       # Dependency checker
│   └── setup_*.sh          # System setup scripts
├── ProtFlow.ipynb          # Main Colab notebook
├── Prokka_ESM3_Workflow*.ipynb  # Prokka workflows
└── README.md               # This file
```

### Key Modules

**`seq_parser`** - Sequence parsing and filtering
- `extract_proteins_from_gbk()` - Extract proteins from GenBank
- `filter_and_select()` - Filter by length and select sequences

**`esm3_predict`** - Structure prediction
- `load_esm3_small()` - Load ESM3-sm model
- `predict_pdbs()` - Batch predict structures

**`p2rank`** - Pocket detection
- `run_p2rank_batch()` - Detect pockets in multiple PDBs

**`ligand_prep`** - Ligand preparation
- `smiles_to_pdbqt()` - Convert SMILES to PDBQT
- `convert_ligand()` - Convert various formats

**`vina_dock`** - Molecular docking
- `dock_to_pockets()` - Dock ligand to predicted pockets

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| "Java not found" | `brew install openjdk` (macOS) / `apt install default-jre` (Ubuntu) |
| "OpenBabel not found" | `brew install open-babel` / `apt install openbabel` |
| "Vina not found" | `brew install autodock-vina` / `apt install autodock-vina` |
| ESM3 model fails | Set `HF_TOKEN` environment variable |
| GPU out of memory | Reduce `--limit` or sequence length |

**Debug mode:**
```bash
python -m scripts.runner --log-level DEBUG --log-file debug.log --predict
```

**Check dependencies:**
```bash
python scripts/check_deps.py
```

---

## 📄 License

This repository depends on third-party tools with their own licenses (P2Rank: Apache 2.0, AutoDock Vina: Apache 2.0, OpenBabel: GPL v2, antiSMASH: AGPL v3). Review their licenses before redistribution.

---

## 📖 Citation

If you use ProtFlow in your research, please cite the underlying tools:
- **ESM**: [Evolutionary Scale Modeling](https://github.com/evolutionaryscale/esm)
- **P2Rank**: Krivák & Hoksza (2018). Journal of Cheminformatics, 10(1), 39.
- **AutoDock Vina**: Trott & Olson (2010). Journal of Computational Chemistry, 31(2), 455-461.
- **antiSMASH**: Blin et al. (2023). Nucleic Acids Research, 51(W1), W46-W50.


