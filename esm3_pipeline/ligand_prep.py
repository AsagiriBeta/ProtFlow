"""
Ligand preparation utilities with OpenBabel integration.
"""
from pathlib import Path
import subprocess
from typing import Optional
import shutil

from .logger import get_logger
from .exceptions import LigandPreparationError, DependencyError

logger = get_logger(__name__)


def check_obabel_available() -> bool:
    """
    Check if OpenBabel is available on the system.

    Returns:
        True if obabel is available, False otherwise
    """
    return shutil.which('obabel') is not None


def smiles_or_file_to_pdbqt(
    input_str: str,
    base_dir: Path,
    output_name: Optional[str] = None,
    ph: float = 7.4,
    validate: bool = True
) -> Optional[Path]:
    """
    Convert SMILES or a local ligand file to PDBQT using OpenBabel.

    Args:
        input_str: SMILES string or path to ligand file
        base_dir: Base directory for output files
        output_name: Custom output filename (without extension)
        ph: pH for protonation state
        validate: Validate the output PDBQT file

    Returns:
        Path to PDBQT file or None if conversion fails

    Raises:
        LigandPreparationError: If preparation fails
        DependencyError: If OpenBabel is not available
    """
    if not input_str:
        logger.warning("Empty input string provided")
        return None

    if not check_obabel_available():
        raise DependencyError("OpenBabel (obabel) is required but not found in PATH")

    base_dir.mkdir(parents=True, exist_ok=True)

    try:
        in_path = Path(input_str)

        if in_path.exists():
            # Input is a file
            logger.info(f"Converting ligand file: {in_path}")
            name = output_name or in_path.stem

            # Convert to PDB first
            lig_pdb = base_dir / f'{name}.pdb'
            result = subprocess.run(
                ['obabel', str(in_path), '-O', str(lig_pdb)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise LigandPreparationError(f"Failed to convert to PDB: {result.stderr}")

            logger.debug(f"Converted to PDB: {lig_pdb}")
        else:
            # Input is SMILES
            logger.info(f"Converting SMILES: {input_str}")
            name = output_name or 'ligand'

            # Generate 3D structure from SMILES
            lig_sdf = base_dir / f'{name}.sdf'
            result = subprocess.run(
                ['obabel', f'-:{input_str}', '-O', str(lig_sdf), '--gen3D'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise LigandPreparationError(f"Failed to generate 3D from SMILES: {result.stderr}")

            logger.debug(f"Generated 3D structure: {lig_sdf}")

            # Convert to PDB
            lig_pdb = base_dir / f'{name}.pdb'
            result = subprocess.run(
                ['obabel', str(lig_sdf), '-O', str(lig_pdb)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                raise LigandPreparationError(f"Failed to convert SDF to PDB: {result.stderr}")

        # Convert to PDBQT with charges
        lig_pdbqt = base_dir / f'{name}.pdbqt'
        result = subprocess.run(
            ['obabel', str(lig_pdb), '-O', str(lig_pdbqt),
             '--partialcharge', 'gasteiger', '-p', str(ph)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise LigandPreparationError(f"Failed to convert to PDBQT: {result.stderr}")

        # Validate output
        if validate:
            if not lig_pdbqt.exists():
                raise LigandPreparationError("PDBQT file was not created")

            if lig_pdbqt.stat().st_size == 0:
                raise LigandPreparationError("PDBQT file is empty")

            # Check for ATOM records
            with open(lig_pdbqt) as f:
                content = f.read()
                if 'ATOM' not in content and 'HETATM' not in content:
                    raise LigandPreparationError("PDBQT file contains no atoms")

        logger.info(f"Ligand prepared successfully: {lig_pdbqt}")
        return lig_pdbqt

    except subprocess.TimeoutExpired:
        raise LigandPreparationError("Ligand preparation timed out")
    except Exception as e:
        if isinstance(e, (LigandPreparationError, DependencyError)):
            raise
        raise LigandPreparationError(f"Unexpected error during ligand preparation: {e}") from e


def validate_pdbqt(pdbqt_file: Path) -> bool:
    """
    Validate a PDBQT file.

    Args:
        pdbqt_file: Path to PDBQT file

    Returns:
        True if valid, False otherwise
    """
    if not pdbqt_file.exists():
        return False

    try:
        with open(pdbqt_file) as f:
            content = f.read()

            # Check for required sections
            has_atoms = 'ATOM' in content or 'HETATM' in content
            has_root = 'ROOT' in content
            has_torsdof = 'TORSDOF' in content

            return has_atoms and (has_root or has_torsdof)
    except Exception:
        return False


