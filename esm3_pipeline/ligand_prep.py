from pathlib import Path
import subprocess
from typing import Optional


def smiles_or_file_to_pdbqt(input_str: str, base_dir: Path) -> Optional[Path]:
    """Convert SMILES or a local ligand file to PDBQT using OpenBabel. Returns PDBQT path or None."""
    if not input_str:
        return None

    in_path = Path(input_str)
    if in_path.exists():
        lig_pdb = base_dir / f'{in_path.stem}.pdb'
        subprocess.run(f"obabel '{in_path}' -O '{lig_pdb}'", shell=True)
        lig_pdbqt = base_dir / f'{in_path.stem}.pdbqt'
        subprocess.run(f"obabel '{lig_pdb}' -O '{lig_pdbqt}' --partialcharge gasteiger", shell=True)
        return lig_pdbqt
    else:
        lig_sdf = base_dir / 'ligand.sdf'
        subprocess.run(f"obabel -:\"{input_str}\" -O \"{lig_sdf}\" --gen3D", shell=True)
        lig_pdb = base_dir / 'ligand.pdb'
        subprocess.run(f"obabel '{lig_sdf}' -O '{lig_pdb}'", shell=True)
        lig_pdbqt = base_dir / 'ligand.pdbqt'
        subprocess.run(f"obabel '{lig_pdb}' -O '{lig_pdbqt}' --partialcharge gasteiger", shell=True)
        return lig_pdbqt

