"""
P2Rank pocket detection utilities with robust error handling.
"""
from pathlib import Path
import subprocess
import pandas as pd
from typing import List, Dict, Optional
import shutil

from .logger import get_logger
from .exceptions import PocketDetectionError, DependencyError

logger = get_logger(__name__)


def check_java_available() -> bool:
    """
    Check if Java is available on the system.

    Returns:
        True if Java is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['java', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ensure_p2rank(
    base_dir: Path,
    version: str = '2.5.1',
    force_download: bool = False
) -> Optional[Path]:
    """
    Ensure P2Rank is downloaded and return path to jar file.

    Args:
        base_dir: Base directory for P2Rank installation
        version: P2Rank version to download
        force_download: Force re-download even if exists

    Returns:
        Path to p2rank.jar or None if download fails

    Raises:
        DependencyError: If Java is not available
    """
    if not check_java_available():
        raise DependencyError("Java is required for P2Rank but not found in PATH")

    p2_dir = base_dir / 'p2rank'
    p2_dir.mkdir(exist_ok=True, parents=True)

    # Check if already exists
    candidates = list(p2_dir.glob('**/p2rank.jar'))
    if candidates and not force_download:
        logger.info(f"P2Rank found at {candidates[0]}")
        return candidates[0]

    logger.info(f"Downloading P2Rank version {version}")

    zip_path = base_dir / f'p2rank-{version}.zip'
    url = f'https://github.com/rdk/p2rank/releases/download/v{version}/p2rank-{version}.zip'

    try:
        # Check if wget is available
        if shutil.which('wget'):
            subprocess.run(
                ['wget', '-q', '-O', str(zip_path), url],
                check=True,
                timeout=300
            )
        elif shutil.which('curl'):
            subprocess.run(
                ['curl', '-L', '-o', str(zip_path), url],
                check=True,
                timeout=300
            )
        else:
            logger.warning("Neither wget nor curl found, trying urllib")
            import urllib.request
            urllib.request.urlretrieve(url, zip_path)

        logger.info("Download complete, extracting...")
        subprocess.run(
            ['unzip', '-q', str(zip_path), '-d', str(p2_dir)],
            check=True
        )

        candidates = list(p2_dir.glob('**/p2rank.jar'))
        if candidates:
            logger.info(f"P2Rank installed successfully at {candidates[0]}")
            return candidates[0]
        else:
            logger.error("P2Rank jar not found after extraction")
            return None

    except subprocess.TimeoutExpired:
        logger.error("Download timed out")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to download/extract P2Rank: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading P2Rank: {e}")
        return None


def run_p2rank_on_pdbs(
    p2rank_jar: Path,
    pdb_dir: Path,
    threads: int = 2,
    visualizations: int = 0,
    top_n_pockets: int = 1
) -> List[Dict]:
    """
    Run P2Rank pocket detection on all PDB files.

    Args:
        p2rank_jar: Path to p2rank.jar
        pdb_dir: Directory containing PDB files
        threads: Number of threads for P2Rank
        visualizations: Visualization level (0=none)
        top_n_pockets: Number of top pockets to extract per protein

    Returns:
        List of dictionaries with pocket information

    Raises:
        PocketDetectionError: If pocket detection fails critically
    """
    if not p2rank_jar.exists():
        raise PocketDetectionError(f"P2Rank jar not found: {p2rank_jar}")

    results: List[Dict] = []
    pdb_files = sorted(pdb_dir.glob('*.pdb'))

    if not pdb_files:
        logger.warning(f"No PDB files found in {pdb_dir}")
        return results

    logger.info(f"Running P2Rank on {len(pdb_files)} PDB files")

    for pdb in pdb_files:
        try:
            outdir = pdb_dir / f'{pdb.stem}_p2'
            outdir.mkdir(exist_ok=True)

            cmd = [
                'java', '-jar', str(p2rank_jar),
                'predict',
                '-f', str(pdb),
                '-o', str(outdir),
                '-threads', str(threads),
                '-visualizations', str(visualizations)
            ]

            logger.debug(f"Running P2Rank for {pdb.name}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300
            )

            if result.returncode != 0:
                logger.warning(f"P2Rank failed for {pdb.name}: {result.stderr.decode()}")
                continue

            # Parse results
            csv_files = list(outdir.glob('*_predictions.csv'))
            if not csv_files:
                logger.warning(f"No prediction CSV found for {pdb.name}")
                continue

            df = pd.read_csv(csv_files[0])
            if df.empty:
                logger.warning(f"Empty predictions for {pdb.name}")
                continue

            # Extract top N pockets
            for idx, row in df.head(top_n_pockets).iterrows():
                results.append({
                    'pdb': str(pdb),
                    'pocket_rank': int(idx) + 1,
                    'center': (float(row['center_x']), float(row['center_y']), float(row['center_z'])),
                    'score': float(row['score']),
                    'probability': float(row.get('probability', 0.0)),
                    'csv': str(csv_files[0])
                })

            logger.debug(f"Extracted {len(df.head(top_n_pockets))} pockets from {pdb.name}")

        except subprocess.TimeoutExpired:
            logger.error(f"P2Rank timed out for {pdb.name}")
            continue
        except Exception as e:
            logger.error(f"Error processing {pdb.name}: {e}")
            continue

    logger.info(f"P2Rank complete: {len(results)} pockets detected")
    return results

