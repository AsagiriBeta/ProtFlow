from pathlib import Path
import subprocess
import pandas as pd
from typing import List, Dict, Tuple
import ast


def ensure_receptor_pdbqt(pdb_path: Path) -> Path:
    pdbqt = pdb_path.with_suffix('.pdbqt')
    if not pdbqt.exists():
        subprocess.run(f"obabel '{pdb_path}' -O '{pdbqt}' --partialcharge gasteiger", shell=True)
    return pdbqt


def run_vina(ligand_pdbqt: Path, pockets: pd.DataFrame, out_base: Path, box_size: int = 20) -> pd.DataFrame:
    rows: List[Dict] = []
    for _, row in pockets.iterrows():
        pdb = Path(row['pdb'])
        receptor = ensure_receptor_pdbqt(pdb)
        cx, cy, cz = row['center'] if not isinstance(row['center'], str) else ast.literal_eval(row['center'])
        outp = out_base / f'dock_{pdb.stem}.out.pdbqt'
        logf = out_base / f'dock_{pdb.stem}.log'
        cmd = (
            f"vina --receptor '{receptor}' --ligand '{ligand_pdbqt}' "
            f"--center_x {cx} --center_y {cy} --center_z {cz} "
            f"--size_x {box_size} --size_y {box_size} --size_z {box_size} "
            f"--out '{outp}' --log '{logf}'"
        )
        subprocess.run(cmd, shell=True)
        aff = None
        if logf.exists():
            for L in open(logf):
                if 'REMARK VINA RESULT:' in L:
                    parts = L.split()
                    try:
                        aff = float(parts[3])
                    except Exception:
                        pass
        rows.append({'pdb': str(pdb), 'out': str(outp), 'log': str(logf), 'affinity': aff})
    dfg = pd.DataFrame(rows)
    return dfg
