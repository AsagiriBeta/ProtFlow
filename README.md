# Modular pipeline for protein structure prediction, pocket detection, ligand docking, and BGC annotation

A modular toolkit to parse GenBank proteins, predict structures with ESM3-sm, detect pockets (P2Rank), prepare ligands and dock (Vina), generate reports, and optionally run antiSMASH—each step is optional and can be run independently.

[中文文档 (Chinese README)](README_zh.md)

This repo provides a Colab-friendly and local runnable pipeline to:
- Parse GenBank files to extract protein CDS translations
- Predict structure PDBs with ESM3 small (`esm3-sm-open-v1`)
- Detect binding pockets with P2Rank
- Prepare ligands (SMILES or SDF/MOL/PDB) and dock with AutoDock Vina
- Produce a compact PDF report
- Optional: Run antiSMASH on GBK/GBFF to annotate biosynthetic gene clusters

The main workflow lives in `ESM3_sm_pipeline-2.ipynb`.

## New: Modular Python package and CLI

You can now run any step independently via a CLI:

```bash
python -m scripts.runner --parse-gbk --predict --p2rank --vina --report \
  --gbk-dir ./esm3_pipeline/gbk_input --smiles "CCO" --limit 5
```

All flags are optional:
- `--parse-gbk` parse GenBank files from `--gbk-dir`
- `--predict` run ESM3-sm to produce PDBs into `esm3_pipeline/pdbs`
- `--p2rank` score pockets
- `--vina` run docking if ligand and pockets are available
- `--report` build `esm3_results_report.pdf`
- `--antismash` run optional antiSMASH (requires it to be installed)

The implementation lives in the `esm3_pipeline/` package. The CLI writes outputs under `esm3_pipeline/`.

## antiSMASH (optional)

antiSMASH isn’t in `requirements.txt`. Install it via Bioconda (recommended) or Docker.

- Option A (Bioconda, recommended)
  ```zsh
  conda config --add channels conda-forge
  conda config --add channels bioconda
  conda create -y -n antismash antismash
  conda activate antismash
  download-antismash-databases
  # optional warm-up caches
  antismash --prepare-data
  antismash --version
  ```

- Option B (Docker, standalone full image with databases; large download)
  ```zsh
  mkdir -p ~/bin
  curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
  chmod a+x ~/bin/run_antismash
  # Use absolute paths; args order is fixed: input first, then output dir
  run_antismash /abs/path/input.gbk /abs/path/out --taxon bacteria
  ```
  For the lite image, download databases separately per the official docs.

Run with this repo’s CLI:
```zsh
# from repo root, in an environment where antismash is installed
conda activate antismash
python -m scripts.runner --antismash --gbk-dir ./esm3_pipeline/gbk_input
```
Outputs go to `esm3_pipeline/antismash_out` (usually includes `index.html`).

Troubleshooting (quick):
- “antismash: command not found”: ensure `conda activate antismash` and PATH is correct.
- Slow first run or missing DBs: run `download-antismash-databases` and `antismash --prepare-data`.
- Docker wrapper requires absolute paths; argument order is input → output.
- Apple Silicon works with Bioconda; Docker may use amd64 images (first run slower).

### Apple Silicon (macOS arm64) note
- On arm64, Bioconda may fail to solve due to `hmmer2` not being available for `osx-arm64`.
- Two working options:
  1) Prefer Docker wrapper (no conda needed): install Docker Desktop, then use `run_antismash` as shown above. Our code auto-detects the wrapper.
  2) Use a Rosetta x86_64 conda env:
     ```zsh
     softwareupdate --install-rosetta --agree-to-license # once, if not installed
     arch -x86_64 zsh -c 'CONDA_SUBDIR=osx-64 conda create -y -n antismash antismash'
     conda activate antismash
     conda config --env --set subdir osx-64
     download-antismash-databases
     antismash --prepare-data && antismash --version
     ```

## Requirements
- Python 3.9–3.11 recommended
- See `requirements.txt` for Python packages
- System tools:
  - Java (JRE) for P2Rank
  - OpenBabel (obabel)
  - AutoDock Vina (vina)
  - (Colab only) `apt-get` is used to install system tools

ESM3-sm access requires a Hugging Face token with permissions to `esm3-sm-open-v1`.

### Dependencies overview (concise)
- Python packages (see versions in `requirements.txt`):
  - esm, huggingface_hub, biopython, pandas, numpy, tqdm, requests, reportlab
  - rdkit-pypi, py3Dmol, matplotlib (optional/convenience)
  - notebook, ipykernel (for local .ipynb execution)
  - torch (on Linux we do not auto-install; choose a CPU/CUDA/MPS build appropriate for your platform)
- System tools: Java (for P2Rank), OpenBabel (obabel), AutoDock Vina (vina), wget/unzip (Colab/Ubuntu only)

## Quickstart (Google Colab)
1. Open the notebook in Colab.
2. Runtime → Change runtime type → GPU.
3. Run Cell 1 to install dependencies (uses `pip` and `apt-get`).
4. Set your token via environment variable or interactive login in Cell 2:
   - Recommended: add a secret named `HF_TOKEN` and run `import os; os.environ['HF_TOKEN'] = 'hf_...'` before Cell 2
5. Upload `.gbk`/`.gbff` files into the `gbk_input` folder as prompted or paste a sequence when asked.
6. Continue through the cells.

## Quickstart (macOS / Linux local)
- Install Python deps:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

- Install PyTorch appropriate to your device:
  - macOS (Apple Silicon):
    - `pip install torch` (MPS acceleration available by default on recent versions)
  - Linux CPU only:
    - `pip install torch==2.4.* --index-url https://download.pytorch.org/whl/cpu`
  - Linux with CUDA (e.g., 12.1):
    - `pip install torch==2.4.* --index-url https://download.pytorch.org/whl/cu121`

- Install system tools using helper scripts:
  - Ubuntu/Debian:
    - `bash scripts/setup_ubuntu.sh`
  - macOS (Homebrew):
    - `bash scripts/setup_macos.sh`

- P2Rank is auto-downloaded in the notebook. Ensure `java -version` works.

- Run the notebook via Jupyter or VS Code/PyCharm:

```
jupyter notebook ESM3_sm_pipeline-2.ipynb
```

## Environment variables
- `HF_TOKEN`: your Hugging Face access token for `esm3-sm-open-v1`. The notebook reads this if set.
  - Copy `.env.example` to `.env` and set the value if you use dotenv in your IDE.

## Security & portability notes
- Removed hardcoded HF token; the notebook reads `HF_TOKEN` or prompts for interactive login.
- Dynamic BASE path (uses `/content` on Colab and the project directory locally).
- P2Rank jar auto-discovery; no fixed path required.
- Parse coordinates from CSV using `ast.literal_eval` instead of `eval`.

## Limitations
- Installing Torch requires choosing the correct CPU/CUDA/MPS build for your platform (see above).
- AutoDock Vina may not be available via package managers on some platforms; manual installation or building from source may be required.
- On macOS, you may need to add Java/OpenBabel/Vina to your PATH to ensure executables are available.

## GitHub tips
- `.gitignore` excludes generated artifacts (PDB/PDBQT, PDFs, CSVs, downloads) and virtualenvs.
- Do not commit your real `HF_TOKEN`; use `.env` locally and GitHub Secrets in CI.
- Consider adding a CI job to lint/execute a smoke cell if you convert the notebook to a script.

## License
This repository contains a workflow that depends on third-party tools with their own licenses (P2Rank, AutoDock Vina, OpenBabel). Review their licenses before redistribution.
