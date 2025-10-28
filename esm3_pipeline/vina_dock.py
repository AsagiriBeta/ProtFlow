"""
AutoDock Vina docking utilities with robust error handling.
"""
from pathlib import Path
import subprocess
import pandas as pd
from typing import List, Dict, Optional
import ast
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

from .logger import get_logger
from .exceptions import DockingError, DependencyError

logger = get_logger(__name__)


def check_vina_available() -> bool:
    """
    Check if AutoDock Vina is available on the system.

    Returns:
        True if vina is available, False otherwise
    """
    return shutil.which('vina') is not None


def ensure_receptor_pdbqt(pdb_path: Path, force_regenerate: bool = False) -> Path:
    """
    Convert PDB receptor to PDBQT format.

    Args:
        pdb_path: Path to PDB file
        force_regenerate: Force regeneration even if exists

    Returns:
        Path to PDBQT file

    Raises:
        DockingError: If conversion fails
    """
    pdbqt = pdb_path.with_suffix('.pdbqt')

    if pdbqt.exists() and not force_regenerate:
        logger.debug(f"Using existing receptor PDBQT: {pdbqt}")
        return pdbqt

    try:
        result = subprocess.run(
            ['obabel', str(pdb_path), '-O', str(pdbqt), '--partialcharge', 'gasteiger'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise DockingError(f"Failed to convert receptor to PDBQT: {result.stderr}")

        logger.debug(f"Generated receptor PDBQT: {pdbqt}")
        return pdbqt

    except subprocess.TimeoutExpired:
        raise DockingError("Receptor conversion timed out")
    except Exception as e:
        raise DockingError(f"Unexpected error converting receptor: {e}") from e


def parse_vina_output(log_file: Path) -> Optional[float]:
    """
    Parse Vina log file to extract best affinity.

    Args:
        log_file: Path to Vina log file

    Returns:
        Best affinity value (kcal/mol) or None
    """
    if not log_file.exists():
        return None

    try:
        with open(log_file) as f:
            for line in f:
                if 'REMARK VINA RESULT:' in line:
                    parts = line.split()
                    try:
                        return float(parts[3])
                    except (IndexError, ValueError):
                        continue
        return None
    except Exception as e:
        logger.warning(f"Failed to parse Vina log {log_file}: {e}")
        return None


def run_single_docking(
    receptor: Path,
    ligand_pdbqt: Path,
    center: tuple,
    out_file: Path,
    log_file: Path,
    box_size: int = 20,
    exhaustiveness: int = 8,
    num_modes: int = 9
) -> Optional[float]:
    """
    Run a single Vina docking calculation.

    Args:
        receptor: Path to receptor PDBQT
        ligand_pdbqt: Path to ligand PDBQT
        center: Tuple of (x, y, z) coordinates
        out_file: Output PDBQT file
        log_file: Log file
        box_size: Size of docking box
        exhaustiveness: Vina exhaustiveness parameter
        num_modes: Number of binding modes to generate

    Returns:
        Best affinity or None
    """
    cx, cy, cz = center

    cmd = [
        'vina',
        '--receptor', str(receptor),
        '--ligand', str(ligand_pdbqt),
        '--center_x', str(cx),
        '--center_y', str(cy),
        '--center_z', str(cz),
        '--size_x', str(box_size),
        '--size_y', str(box_size),
        '--size_z', str(box_size),
        '--exhaustiveness', str(exhaustiveness),
        '--num_modes', str(num_modes),
        '--out', str(out_file),
        '--log', str(log_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes max per docking
        )

        if result.returncode != 0:
            logger.warning(f"Vina failed for {out_file.stem}: {result.stderr}")
            return None

        return parse_vina_output(log_file)

    except subprocess.TimeoutExpired:
        logger.error(f"Vina timed out for {out_file.stem}")
        return None
    except Exception as e:
        logger.error(f"Docking error for {out_file.stem}: {e}")
        return None


def run_vina(
    ligand_pdbqt: Path,
    pockets: pd.DataFrame,
    out_base: Path,
    box_size: int = 20,
    exhaustiveness: int = 8,
    num_modes: int = 9,
    parallel: bool = False,
    max_workers: int = 4
) -> pd.DataFrame:
    """
    Run Vina docking on multiple pockets.

    Args:
        ligand_pdbqt: Path to ligand PDBQT file
        pockets: DataFrame with pocket information
        out_base: Base directory for outputs
        box_size: Size of docking box
        exhaustiveness: Vina exhaustiveness
        num_modes: Number of binding modes
        parallel: Run docking in parallel
        max_workers: Maximum parallel workers

    Returns:
        DataFrame with docking results

    Raises:
        DockingError: If docking fails critically
        DependencyError: If Vina is not available
    """
    if not check_vina_available():
        raise DependencyError("AutoDock Vina is required but not found in PATH")

    if not ligand_pdbqt.exists():
        raise DockingError(f"Ligand PDBQT not found: {ligand_pdbqt}")

    out_base.mkdir(parents=True, exist_ok=True)

    logger.info(f"Running Vina docking on {len(pockets)} pockets")

    rows: List[Dict] = []

    def dock_pocket(row):
        """Dock to a single pocket."""
        pdb = Path(row['pdb'])
        try:
            receptor = ensure_receptor_pdbqt(pdb)
            center = row['center'] if not isinstance(row['center'], str) else ast.literal_eval(row['center'])

            pocket_rank = row.get('pocket_rank', 1)
            out_file = out_base / f'dock_{pdb.stem}_p{pocket_rank}.pdbqt'
            log_file = out_base / f'dock_{pdb.stem}_p{pocket_rank}.log'

            affinity = run_single_docking(
                receptor, ligand_pdbqt, center,
                out_file, log_file,
                box_size, exhaustiveness, num_modes
            )

            return {
                'pdb': str(pdb),
                'pocket_rank': pocket_rank,
                'out': str(out_file) if out_file.exists() else None,
                'log': str(log_file) if log_file.exists() else None,
                'affinity': affinity,
                'center': center
            }
        except Exception as e:
            logger.error(f"Failed to dock to {pdb.name}: {e}")
            return {
                'pdb': str(pdb),
                'pocket_rank': row.get('pocket_rank', 1),
                'out': None,
                'log': None,
                'affinity': None,
                'center': None
            }

    if parallel and len(pockets) > 1:
        logger.info(f"Running parallel docking with {max_workers} workers")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(dock_pocket, row): idx for idx, row in pockets.iterrows()}
            for future in as_completed(futures):
                rows.append(future.result())
    else:
        for _, row in pockets.iterrows():
            rows.append(dock_pocket(row))

    dfg = pd.DataFrame(rows)

    # Log summary
    successful = dfg['affinity'].notna().sum()
    logger.info(f"Docking complete: {successful}/{len(dfg)} successful")

    if successful > 0:
        best_affinity = dfg['affinity'].min()
        logger.info(f"Best affinity: {best_affinity:.2f} kcal/mol")

    return dfg
