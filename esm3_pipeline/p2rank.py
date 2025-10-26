from pathlib import Path
import subprocess
import pandas as pd
from typing import List, Dict, Tuple


def ensure_p2rank(base_dir: Path) -> Path:
    """Ensure P2Rank is downloaded under base_dir/p2rank and return path to jar."""
    p2_dir = base_dir / 'p2rank'
    p2_dir.mkdir(exist_ok=True)
    candidates = list(p2_dir.glob('**/p2rank.jar'))
    if candidates:
        return candidates[0]

    zip_path = base_dir / 'p2rank-2.5.1.zip'
    url = 'https://github.com/rdk/p2rank/releases/download/v2.5.1/p2rank-2.5.1.zip'
    subprocess.run(['wget','-q','-O', str(zip_path), url], check=False)
    subprocess.run(['unzip','-q', str(zip_path), '-d', str(p2_dir)], check=False)
    candidates = list(p2_dir.glob('**/p2rank.jar'))
    return candidates[0] if candidates else None


def run_p2rank_on_pdbs(p2rank_jar: Path, pdb_dir: Path) -> List[Dict]:
    results: List[Dict] = []
    for pdb in sorted(pdb_dir.glob('*.pdb')):
        outdir = pdb_dir / f'{pdb.stem}_p2'
        outdir.mkdir(exist_ok=True)
        cmd = [
            'java', '-jar', str(p2rank_jar), 'predict', '-f', str(pdb),
            '-o', str(outdir), '-threads', '2', '-visualizations', '0'
        ]
        subprocess.run(cmd)
        csv_files = list(outdir.glob('*_predictions.csv'))
        if not csv_files:
            continue
        df = pd.read_csv(csv_files[0])
        if df.empty:
            continue
        top = df.iloc[0]
        results.append({
            'pdb': str(pdb),
            'center': (float(top['center_x']), float(top['center_y']), float(top['center_z'])),
            'score': float(top['score']),
            'csv': str(csv_files[0])
        })
    return results

