# DALI Structure Alignment

DALI (Distance-matrix ALIgnment) is a powerful tool for protein structure comparison and alignment. ProtFlow now provides comprehensive support for both **online DALI server** and **local DALI installation**.

## Overview

The `protflow.prediction.dali` module provides:
- ✨ **Online DALI server** support (ekhidna2.biocenter.helsinki.fi)
- 🔄 **Automatic fallback** from online to local mode
- 📦 **Batch processing** for multiple structures
- 📊 **Result parsing** and CSV export
- 🎯 **Easy-to-use Python API**

## Quick Start

### Basic Usage

```python
from pathlib import Path
from protflow.prediction.dali import DaliAligner

# Initialize aligner (auto mode - tries online first)
aligner = DaliAligner(mode='auto', output_dir=Path('./outputs/dali'))

# Align a single structure
results = aligner.align(
    query_structure=Path('protein.pdb'),
    database='pdb25',
)

# Print top results
for result in results[:10]:
    print(f"{result.rank}. {result.target_pdb} Z-score: {result.z_score:.2f}")
```

### Batch Processing

```python
from pathlib import Path
from protflow.prediction.dali import batch_align

# Process all PDB files in a directory
results_list = batch_align(
    structures_dir=Path('./data/structures'),
    pattern='*.pdb',
    mode='auto',
)

# results_list is a list of (query_name, results) tuples
for query_name, results in results_list:
    print(f"{query_name}: {len(results)} alignments found")
```

## Modes

### Online Mode

Uses the DALI web server at Helsinki Biocenter.

**Advantages:**
- No local installation required
- Always uses latest PDB database
- No disk space needed for databases
- Ideal for occasional use

**Requirements:**
- Internet connection
- Access to ekhidna2.biocenter.helsinki.fi

```python
aligner = DaliAligner(mode='online')
results = aligner.align(Path('protein.pdb'), database='pdb25')
```

**Available Databases:**
- `pdb25` - Non-redundant at 25% sequence identity (recommended)
- `pdb50` - Non-redundant at 50% sequence identity
- `pdb90` - Non-redundant at 90% sequence identity
- `pdb100` - Complete PDB

### Local Mode

Uses locally installed DALI (dali.pl).

**Advantages:**
- No internet required
- Faster for batch processing
- Full control over database versions
- Can use custom databases

**Requirements:**
- DALI installed locally
- PDB database downloaded (≥50 GB)

```python
aligner = DaliAligner(
    mode='local',
    dali_cmd=Path('/usr/local/bin/dali.pl'),
)
results = aligner.align(Path('protein.pdb'))
```

### Auto Mode (Recommended)

Automatically selects the best available mode.

**Behavior:**
1. Checks if online DALI server is accessible
2. If available, uses online mode
3. If not, falls back to local DALI
4. If neither available, raises an error

```python
aligner = DaliAligner(mode='auto')  # Default
```

## Notebook Usage

The updated DALI notebook (`notebooks/tools/12_structure_alignment_dali.ipynb`) provides a complete workflow:

1. **Configure mode**: Choose online, local, or auto
2. **Sync ESM3 predictions**: Automatically import predicted structures
3. **Batch alignment**: Process all structures at once
4. **Results visualization**: View and export results

### Configuration

```python
# In the notebook
DALI_MODE = 'auto'        # 'online', 'local', or 'auto'
DALI_DATABASE = 'pdb25'   # For online mode
DALI_CMD = None           # Path to dali.pl (None = auto-detect)
```

## API Reference

### DaliAligner Class

```python
class DaliAligner:
    def __init__(
        self,
        mode: str = 'auto',
        dali_cmd: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        timeout: int = 300,
        max_retries: int = 3,
    )
```

**Parameters:**
- `mode`: Operation mode ('online', 'local', or 'auto')
- `dali_cmd`: Path to dali.pl for local mode
- `output_dir`: Directory for output files
- `timeout`: Timeout for online queries (seconds)
- `max_retries`: Maximum retries for failed requests

**Methods:**

#### align()

```python
def align(
    self,
    query_structure: Path,
    database: str = "pdb25",
    output_name: Optional[str] = None,
) -> List[DaliResult]
```

Align a single structure against a database.

#### align_batch()

```python
def align_batch(
    self,
    query_structures: Iterable[Path],
    database: str = "pdb25",
    parallel: bool = False,
) -> List[Tuple[str, List[DaliResult]]]
```

Align multiple structures in batch.

#### summarize_results()

```python
def summarize_results(
    self,
    results_list: List[Tuple[str, List[DaliResult]]],
    top_n: int = 10,
) -> Optional[pd.DataFrame]
```

Create a summary DataFrame from batch results.

### DaliResult Class

```python
@dataclass
class DaliResult:
    query_name: str
    target_pdb: str
    rank: int
    z_score: float
    rmsd: float
    lali: Optional[int] = None     # Alignment length
    nres: Optional[int] = None     # Number of residues
    identity: Optional[float] = None  # Sequence identity %
```

### Convenience Functions

#### run_dali_alignment()

```python
def run_dali_alignment(
    query_structure: Path,
    mode: str = 'auto',
    database: str = 'pdb25',
    output_dir: Optional[Path] = None,
) -> List[DaliResult]
```

One-liner for running DALI alignment.

#### batch_align()

```python
def batch_align(
    structures_dir: Path,
    pattern: str = "*.pdb",
    mode: str = 'auto',
    output_dir: Optional[Path] = None,
) -> List[Tuple[str, List[DaliResult]]]
```

One-liner for batch processing.

## Output Files

Results are saved in the output directory:

```
outputs/dali/
├── protein1_results.csv          # Individual result files
├── protein2_results.csv
├── dali_batch_summary.csv        # Batch summary
└── protein1/                     # Local mode creates subdirs
    └── dali.log
```

### CSV Format

```csv
query,target_pdb,rank,z_score,rmsd,lali,nres,identity
protein1,1ABC,1,45.2,1.8,234,250,25.0
protein1,2DEF,2,42.1,2.1,228,250,23.5
```

## Integration with Workflows

### ESM3 → DALI Pipeline

```python
from pathlib import Path
from protflow.prediction import esm3_predict, dali

# 1. Predict structures with ESM3
predictor = esm3_predict.ESM3Predictor()
predictor.predict_batch(sequences, output_dir=Path('./predictions'))

# 2. Align predicted structures with DALI
aligner = dali.DaliAligner(mode='auto')
results = aligner.align_batch(
    Path('./predictions').glob('*.pdb')
)

# 3. Find similar structures
summary = aligner.summarize_results(results, top_n=5)
print(summary[summary['z_score'] > 10])  # High-confidence matches
```

### CLI Integration

```python
# In your script
import argparse
from protflow.prediction.dali import run_dali_alignment

parser = argparse.ArgumentParser()
parser.add_argument('structure', type=Path)
parser.add_argument('--mode', default='auto')
args = parser.parse_args()

results = run_dali_alignment(args.structure, mode=args.mode)
for r in results[:10]:
    print(f"{r.target_pdb}: Z={r.z_score:.2f}")
```

## Understanding Results

### Z-score

The Z-score measures the statistical significance of the structural similarity:

- **Z > 20**: Highly significant, likely homologous
- **Z > 10**: Significant similarity
- **Z > 5**: Possible similarity
- **Z < 2**: Not significant (random similarity)

### RMSD

Root Mean Square Deviation measures structural difference:
- **Lower is better** (more similar structures)
- Typical range: 1-5 Å for similar proteins
- > 10 Å indicates very different structures

### Example Interpretation

```python
result = results[0]
if result.z_score > 20:
    print(f"Strong match to {result.target_pdb}")
    print(f"RMSD: {result.rmsd:.2f} Å")
    print(f"Alignment length: {result.lali} residues")
    print(f"Sequence identity: {result.identity:.1f}%")
```

## Troubleshooting

### Online Mode Issues

**Problem**: "Online DALI server not available"

**Solutions:**
1. Check internet connection
2. Verify server is accessible: `curl http://ekhidna2.biocenter.helsinki.fi/dali/`
3. Use local mode as fallback
4. Set `mode='auto'` for automatic fallback

### Local Mode Issues

**Problem**: "Local DALI not available"

**Solutions:**
1. Install DALI: Download from [DALI website](http://ekhidna.biocenter.helsinki.fi/dali/)
2. Set DALI_CMD explicitly:
   ```python
   aligner = DaliAligner(mode='local', dali_cmd=Path('/path/to/dali.pl'))
   ```
3. Add dali.pl to PATH
4. Download PDB database

### Timeout Issues

**Problem**: "DALI job did not complete within timeout"

**Solutions:**
```python
aligner = DaliAligner(
    mode='online',
    timeout=600,  # Increase to 10 minutes
)
```

## Performance Tips

### For Batch Processing

1. **Use local mode** for many structures (>10)
2. **Increase timeout** for large structures
3. **Filter by Z-score** to reduce output size
4. **Process in chunks** if you have hundreds of structures

```python
# Process in chunks
from itertools import islice

def chunked(iterable, n):
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk

for chunk in chunked(all_structures, 10):
    results = aligner.align_batch(chunk)
    # Process results...
```

### For Online Mode

1. Use `pdb25` for faster queries (smaller database)
2. Set reasonable timeout (300-600 seconds)
3. Enable retries: `max_retries=3`

### For Local Mode

1. Use SSD for database storage
2. Ensure sufficient RAM (≥8 GB)
3. Run batch processing overnight for large datasets

## Advanced Usage

### Custom Result Filtering

```python
# Filter by Z-score and RMSD
high_quality = [
    r for r in results
    if r.z_score > 15 and r.rmsd < 3.0
]

# Group by Z-score ranges
import pandas as pd
df = pd.DataFrame([r.to_dict() for r in results])
df['score_range'] = pd.cut(df['z_score'], bins=[0, 5, 10, 20, 100])
print(df.groupby('score_range').size())
```

### Integration with Structure Visualization

```python
import py3Dmol

# Visualize top hit
top_hit = results[0]
viewer = py3Dmol.view(width=800, height=600)
viewer.addModel(open(f'{top_hit.target_pdb}.pdb').read(), 'pdb')
viewer.setStyle({'cartoon': {'color': 'spectrum'}})
viewer.show()
```

## References

- **DALI Server**: http://ekhidna2.biocenter.helsinki.fi/dali/
- **DALI Paper**: Holm, L. (2020). DALI and the persistence of protein shape. *Protein Science*, 29(1), 128-140.
- **PDB**: https://www.rcsb.org/

## See Also

- [ESM3 Structure Prediction](./esm3-prediction.md)
- [Structure Analysis](../user-guide/tutorial/advanced-features.md)
- [Complete Workflows](../user-guide/notebook-index.md)
