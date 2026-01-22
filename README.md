# ProtFlow

A modular pipeline for protein structure prediction, pocket detection, and ligand docking.

**📖 [中文文档](README_zh.md)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/00_genome_annotation_to_structure.ipynb)

---

## 🚀 Available Workflows

### 📂 Notebook Organization
All notebooks are now organized in `/notebooks/` with systematic numbering:
- **Core workflows** (00-09): Complete analysis pipelines
- **Tools** (10-19): Individual analysis tools
- **Analysis** (20-29): Result analysis and comparison tools

### 1. **Core Workflows** - Complete Pipelines

#### 🧬 **Prokka → ESM3 → DALI** (Recommended)
- **Flow**: FNA → Prokka → ESM3 → DALI-ready PDBs
- **Notebook**: [`notebooks/core/00_genome_annotation_to_structure.ipynb`](notebooks/core/00_genome_annotation_to_structure.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/00_genome_annotation_to_structure.ipynb)
- **Use**: Genome annotation, structural proteomics

#### 🎯 **Structure Prediction & Analysis**
- **Flow**: Protein sequences → ESM3 → Structure analysis
- **Notebook**: [`notebooks/core/01_protein_structure_prediction.ipynb`](notebooks/core/01_protein_structure_prediction.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/01_protein_structure_prediction.ipynb)
- **Use**: Protein structure prediction and analysis

#### 🔍 **Pocket Detection & Analysis**
- **Flow**: PDB structures → P2Rank → Pocket analysis
- **Notebook**: [`notebooks/core/02_pocket_detection_p2rank.ipynb`](notebooks/core/02_pocket_detection_p2rank.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/02_pocket_detection_p2rank.ipynb)
- **Use**: Binding site detection and analysis

#### ⚗️ **Ligand Docking & Analysis**
- **Flow**: PDB + Ligands → Vina → Docking analysis
- **Notebook**: [`notebooks/core/03_ligand_docking_vina.ipynb`](notebooks/core/03_ligand_docking_vina.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/03_ligand_docking_vina.ipynb)
- **Use**: Molecular docking and binding analysis

### 2. **Individual Tools** - Standalone Analysis

#### 📝 **Genome Annotation (Prokka)**
- **Tool**: Prokka genome annotation
- **Notebook**: [`notebooks/tools/10_genome_annotation_prokka.ipynb`](notebooks/tools/10_genome_annotation_prokka.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/10_genome_annotation_prokka.ipynb)
- **Use**: Bacterial genome annotation

#### 🧪 **Protein Structure Prediction (ESM3)**
- **Tool**: ESM3 structure prediction
- **Notebook**: [`notebooks/tools/11_protein_structure_esm3.ipynb`](notebooks/tools/11_protein_structure_esm3.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/11_protein_structure_esm3.ipynb)
- **Use**: Individual protein structure prediction

#### 📊 **Structure Alignment (DALI)**
- **Tool**: DALI structure alignment
- **Notebook**: [`notebooks/tools/12_structure_alignment_dali.ipynb`](notebooks/tools/12_structure_alignment_dali.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/12_structure_alignment_dali.ipynb)
- **Use**: Protein structure comparison

#### 🧬 **BGC Analysis (antiSMASH)**
- **Tool**: antiSMASH BGC detection
- **Notebook**: [`notebooks/tools/13_biosynthetic_cluster_antismash.ipynb`](notebooks/tools/13_biosynthetic_cluster_antismash.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/13_biosynthetic_cluster_antismash.ipynb)
- **Use**: Antibiotic gene cluster analysis

### 3. **Analysis Tools** - Result Processing

#### 📈 **CDS Annotation Comparison**
- **Tool**: Compare different annotation results
- **Notebook**: [`notebooks/analysis/20_cds_annotation_comparison.ipynb`](notebooks/analysis/20_cds_annotation_comparison.ipynb)
- **Use**: Annotation quality assessment

#### 📊 **Batch Structure Analysis**
- **Tool**: Analyze multiple structures
- **Notebook**: [`notebooks/analysis/21_batch_structure_analysis.ipynb`](notebooks/analysis/21_batch_structure_analysis.ipynb)
- **Use**: Large-scale structure analysis

#### 🔬 **Structure Comparison (TM-align)**
- **Tool**: TM-align structure comparison
- **Notebook**: [`notebooks/analysis/22_structure_comparison_tm_align.ipynb`](notebooks/analysis/22_structure_comparison_tm_align.ipynb)
- **Use**: Batch structure comparison and quality assessment

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
python -m protflow.cli.runner --parse-gbk --predict --limit 5
# Or use the installed command:
protflow --parse-gbk --predict --limit 5

# Or launch JupyterLab with all notebooks
jupyter lab notebooks/
```

**For Prokka workflow on JupyterLab:**
```bash
# Install micromamba (if needed)
brew install micromamba  # macOS
# or: curl -Ls https://micro.mamba.pm/install.sh | bash

# Create Prokka environment
micromamba create -y -n prokka -c bioconda prokka python=3.10
micromamba run -n prokka prokka --setupdb

# Launch notebook navigator
jupyter lab notebooks/
# Then navigate to: notebooks/core/00_genome_annotation_to_structure.ipynb
```

**For JupyterLab with CUDA on remote servers:**

If you encounter `nvcc: not found` or PyTorch can't detect CUDA in venv:

```bash
# 1. Upload and run CUDA setup script
chmod +x setup_cuda_env.sh
./setup_cuda_env.sh ~/jupyter-env-3.12  # Replace with your venv path

# 2. Restart JupyterLab
pkill -f jupyter
source ~/jupyter-env-3.12/bin/activate
jupyter lab notebooks/
```

See `config/config.example.json` for configuration options.

---

## 💡 Usage Examples

### CLI Pipeline
```bash
# Full pipeline: parse → predict → DALI alignment → dock → report
protflow --parse-gbk --predict --dali --p2rank --vina --report --smiles "CCO" --limit 5
# Or: python -m protflow.cli.runner --parse-gbk --predict --dali --p2rank --vina --report --smiles "CCO" --limit 5

# Prokka → ESM3 → DALI workflow (recommended for structure exploration)
protflow --parse-gbk --predict --dali --limit 10

# Structure prediction only
protflow --predict --limit 10

# DALI online alignment
protflow --predict --dali --dali-mode online --dali-database pdb25

# Docking with custom ligand
protflow --vina --ligand my_drug.mol2 --parallel

# antiSMASH BGC analysis
protflow --antismash --gbk-dir ./genomes
```

**CLI Options:**
```bash
# Workflow steps (run any combination)
--parse-gbk          # Extract proteins from GenBank files
--predict            # Predict 3D structures with ESM3
--dali               # Run DALI structure alignment (NEW!)
--p2rank             # Detect binding pockets
--vina               # Run molecular docking
--report             # Generate PDF report
--antismash          # Run antiSMASH BGC analysis

# DALI Options
--dali-mode MODE     # DALI mode: online, local, auto (default: auto)
--dali-database DB   # Online database: pdb25, pdb50, pdb90, pdb100 (default: pdb25)
--dali-cmd PATH      # Path to local dali.pl

# Input/Output
--gbk-dir DIR        # GenBank files directory (default: ./data/inputs)
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
from protflow.utils.seq_parser import extract_proteins_from_gbk, filter_and_select
from protflow.prediction.esm3_predict import load_esm3_small, predict_pdbs
from protflow.docking import p2rank, vina_dock, ligand_prep

# 1. Parse GenBank files
n = extract_proteins_from_gbk(
    Path("./data/inputs"), 
    Path("./proteins.faa")
)

# 2. Filter and select sequences
selected = filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=5
)

# 3. Predict structures
model, device = load_esm3_small()
predict_pdbs(model, selected, Path("./outputs/structures"))

# 4. Detect pockets
p2rank.run_p2rank_batch(Path("./outputs/structures"), Path("./outputs/pockets"))

# 5. Dock ligand
ligand = ligand_prep.smiles_to_pdbqt("CCO", Path("./ligand.pdbqt"))
vina_dock.dock_to_pockets(
    Path("./outputs/structures/protein.pdb"),
    ligand,
    Path("./outputs/pockets/protein_predictions.csv"),
    Path("./outputs/docking")
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
Run: `protflow --config config/config.example.json --predict --report`

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

✅ **Completely Reorganized** - Systematic notebook numbering and organization  
✅ **Modular Design** - Run any step independently  
✅ **High Performance** - GPU acceleration, caching, parallel processing, batch processing  
✅ **Flexible Input** - GenBank, FASTA, SMILES, molecular files  
✅ **Production Ready** - Structured logging, error handling, testing  
✅ **Unified CLI** - All command-line tools in `protflow.cli` module  
✅ **Multi-language Support** - English and Chinese README

### Project Structure
```
ProtFlow/
├── notebooks/                    # Jupyter notebooks (completely reorganized)
│   ├── core/                    # Core analysis workflows (00-09)
│   │   ├── 00_genome_annotation_to_structure.ipynb
│   │   ├── 01_protein_structure_prediction.ipynb
│   │   ├── 02_pocket_detection_p2rank.ipynb
│   │   └── 03_ligand_docking_vina.ipynb
│   ├── tools/                   # Individual analysis tools (10-19)
│   │   ├── 10_genome_annotation_prokka.ipynb
│   │   ├── 11_protein_structure_esm3.ipynb
│   │   ├── 12_structure_alignment_dali.ipynb
│   │   └── 13_biosynthetic_cluster_antismash.ipynb
│   └── analysis/                # Result analysis tools (20-29)
│       ├── 20_cds_annotation_comparison.ipynb
│       ├── 21_batch_structure_analysis.ipynb
│       └── 22_structure_comparison_tm_align.ipynb
├── src/protflow/                # Python source code (modular)
│   ├── core/                    # Core functionality
│   ├── prediction/              # Structure prediction
│   ├── docking/                 # Molecular docking
│   ├── visualization/           # Visualization tools
│   ├── utils/                   # Utility modules
│   └── cli/                     # Command line tools
├── config/                      # Configuration files
├── data/                        # Input data directory
├── outputs/                     # Output results directory
├── notebooks/                   # Jupyter notebooks
├── tests/                       # Test files
└── README.md                    # This file
```

### Key Modules

**`protflow.core`** - Core functionality and data management
- Genome annotation and processing
- Result aggregation and reporting

**`protflow.prediction`** - Structure prediction
- `esm3_predict.py` - ESM3-based structure prediction
- Batch processing capabilities

**`protflow.docking`** - Molecular docking and pocket detection
- `p2rank.py` - Binding site prediction
- `vina_dock.py` - Molecular docking
- `ligand_prep.py` - Ligand preparation

**`protflow.visualization`** - Data visualization
- Structure visualization
- Analysis result plotting

**`protflow.utils`** - Utility modules
- `config.py` - Configuration management
- `logger.py` - Logging utilities
- `seq_parser.py` - Sequence parsing and filtering
- `notebook_utils.py` - Notebook utilities

**`protflow.cli`** - Command line tools
- `runner.py` - Main pipeline runner
- `check_deps.py` - Dependency checker
- `validate_notebook.py` - Notebook validator
- `tm_align_comparison.py` - Structure comparison tools

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
protflow --log-level DEBUG --log-file debug.log --predict
```

**Check dependencies:**
```bash
protflow-check-deps
# Or: python -m protflow.cli.check_deps
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


