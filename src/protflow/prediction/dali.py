"""
DALI Structure Alignment Module

Provides support for both online DALI server and local DALI installation.
Supports batch processing, result parsing, and automatic mode fallback.

Online DALI Server: http://ekhidna2.biocenter.helsinki.fi/dali/
Local DALI: Requires dali.pl or equivalent installed locally

Author: ProtFlow Contributors
"""

import logging
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union
import requests

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

logger = logging.getLogger(__name__)


@dataclass
class DaliResult:
    """Container for DALI alignment results."""
    query_name: str
    target_pdb: str
    rank: int
    z_score: float
    rmsd: float
    lali: Optional[int] = None  # Length of alignment
    nres: Optional[int] = None  # Number of residues
    identity: Optional[float] = None  # Sequence identity %
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'query': self.query_name,
            'target_pdb': self.target_pdb,
            'rank': self.rank,
            'z_score': self.z_score,
            'rmsd': self.rmsd,
            'lali': self.lali,
            'nres': self.nres,
            'identity': self.identity,
        }


class DaliAligner:
    """
    DALI structure alignment tool supporting both online and local modes.
    
    Examples:
        # Online mode (default)
        aligner = DaliAligner(mode='online')
        results = aligner.align(Path('protein.pdb'))
        
        # Local mode
        aligner = DaliAligner(mode='local', dali_cmd='/path/to/dali.pl')
        results = aligner.align(Path('protein.pdb'))
        
        # Batch processing
        results_list = aligner.align_batch([Path('p1.pdb'), Path('p2.pdb')])
    """
    
    ONLINE_SERVER = "http://ekhidna2.biocenter.helsinki.fi/dali/"
    DEFAULT_TIMEOUT = 300  # 5 minutes for online queries
    POLL_INTERVAL = 10  # Check status every 10 seconds
    
    def __init__(
        self,
        mode: str = 'auto',
        dali_cmd: Optional[Union[str, Path]] = None,
        output_dir: Optional[Path] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        """
        Initialize DALI aligner.
        
        Args:
            mode: 'online', 'local', or 'auto' (try online first, fallback to local)
            dali_cmd: Path to local dali.pl script (for local mode)
            output_dir: Directory for output files (default: ./outputs/dali)
            timeout: Timeout for online queries in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.mode = mode.lower()
        if self.mode not in ['online', 'local', 'auto']:
            raise ValueError(f"Invalid mode: {mode}. Must be 'online', 'local', or 'auto'")
        
        self.dali_cmd = Path(dali_cmd) if dali_cmd else self._find_dali_cmd()
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "outputs" / "dali"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Validate setup
        if self.mode == 'local' and not self._check_local_dali():
            raise RuntimeError("Local DALI not available. Install DALI or use online mode.")
        
        logger.info(f"DALI aligner initialized in {self.mode} mode")
    
    def _find_dali_cmd(self) -> Optional[Path]:
        """Find dali.pl in PATH."""
        dali_path = shutil.which("dali.pl")
        if dali_path:
            return Path(dali_path)
        # Check common locations
        common_paths = [
            Path("/usr/local/bin/dali.pl"),
            Path("/opt/dali/dali.pl"),
            Path.home() / "bin" / "dali.pl",
        ]
        for path in common_paths:
            if path.exists():
                return path
        return None
    
    def _check_local_dali(self) -> bool:
        """Check if local DALI is available."""
        if not self.dali_cmd or not self.dali_cmd.exists():
            logger.warning("DALI command not found")
            return False
        try:
            result = subprocess.run(
                [str(self.dali_cmd), "--help"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0 or "dali" in result.stdout.decode().lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_online_availability(self) -> bool:
        """Check if online DALI server is accessible."""
        try:
            response = requests.get(self.ONLINE_SERVER, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Online DALI server not accessible: {e}")
            return False
    
    def align(
        self,
        query_structure: Path,
        database: str = "pdb25",
        output_name: Optional[str] = None,
    ) -> List[DaliResult]:
        """
        Align a query structure against a database.
        
        Args:
            query_structure: Path to PDB/CIF structure file
            database: Database to search against (for online: pdb25, pdb50, pdb90, pdb100)
            output_name: Name for output files (default: query filename stem)
            
        Returns:
            List of DaliResult objects sorted by Z-score
        """
        if not query_structure.exists():
            raise FileNotFoundError(f"Query structure not found: {query_structure}")
        
        output_name = output_name or query_structure.stem
        
        # Determine actual mode to use
        actual_mode = self._determine_mode()
        
        if actual_mode == 'online':
            return self._align_online(query_structure, database, output_name)
        else:
            return self._align_local(query_structure, output_name)
    
    def _determine_mode(self) -> str:
        """Determine which mode to actually use based on availability."""
        if self.mode == 'online':
            if not self._check_online_availability():
                raise RuntimeError("Online DALI server not available")
            return 'online'
        elif self.mode == 'local':
            return 'local'
        else:  # auto mode
            if self._check_online_availability():
                logger.info("Using online DALI server")
                return 'online'
            elif self._check_local_dali():
                logger.info("Falling back to local DALI")
                return 'local'
            else:
                raise RuntimeError("Neither online nor local DALI available")
    
    def _align_online(
        self,
        query_structure: Path,
        database: str,
        output_name: str,
    ) -> List[DaliResult]:
        """
        Perform alignment using online DALI server.
        
        Uses the DALI web service API to submit jobs and retrieve results.
        """
        logger.info(f"Submitting {query_structure.name} to online DALI server...")
        
        # Submit job
        job_id = self._submit_online_job(query_structure, database)
        
        # Poll for results
        logger.info(f"Job submitted with ID: {job_id}. Waiting for completion...")
        results_data = self._poll_online_results(job_id)
        
        # Parse and save results
        results = self._parse_online_results(results_data, output_name)
        
        # Save results locally
        self._save_results(results, output_name)
        
        logger.info(f"Found {len(results)} alignments for {query_structure.name}")
        return results
    
    def _submit_online_job(self, query_structure: Path, database: str) -> str:
        """Submit job to DALI online server."""
        submit_url = f"{self.ONLINE_SERVER}api/submit"
        
        with open(query_structure, 'rb') as f:
            files = {'pdbfile': (query_structure.name, f, 'application/octet-stream')}
            data = {'database': database}
            
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        submit_url,
                        files=files,
                        data=data,
                        timeout=30,
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result['job_id']
                except requests.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise RuntimeError(f"Failed to submit DALI job: {e}")
                    logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(5)
    
    def _poll_online_results(self, job_id: str) -> Dict:
        """Poll for job completion and retrieve results."""
        status_url = f"{self.ONLINE_SERVER}api/status/{job_id}"
        result_url = f"{self.ONLINE_SERVER}api/result/{job_id}"
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                response = requests.get(status_url, timeout=10)
                response.raise_for_status()
                status = response.json()
                
                if status['status'] == 'completed':
                    # Fetch results
                    result_response = requests.get(result_url, timeout=30)
                    result_response.raise_for_status()
                    return result_response.json()
                elif status['status'] == 'failed':
                    raise RuntimeError(f"DALI job failed: {status.get('error', 'Unknown error')}")
                
                # Still running, wait and retry
                time.sleep(self.POLL_INTERVAL)
            except requests.RequestException as e:
                logger.warning(f"Error polling status: {e}")
                time.sleep(self.POLL_INTERVAL)
        
        raise TimeoutError(f"DALI job {job_id} did not complete within {self.timeout}s")
    
    def _parse_online_results(self, results_data: Dict, query_name: str) -> List[DaliResult]:
        """Parse results from online DALI server."""
        results = []
        
        for idx, hit in enumerate(results_data.get('hits', []), start=1):
            result = DaliResult(
                query_name=query_name,
                target_pdb=hit.get('pdbid', ''),
                rank=idx,
                z_score=float(hit.get('z', 0.0)),
                rmsd=float(hit.get('rmsd', 0.0)),
                lali=int(hit.get('lali', 0)) if hit.get('lali') else None,
                nres=int(hit.get('nres', 0)) if hit.get('nres') else None,
                identity=float(hit.get('id', 0.0)) if hit.get('id') else None,
            )
            results.append(result)
        
        return sorted(results, key=lambda x: x.z_score, reverse=True)
    
    def _align_local(self, query_structure: Path, output_name: str) -> List[DaliResult]:
        """
        Perform alignment using local DALI installation.
        
        Executes dali.pl and parses the output files.
        """
        logger.info(f"Running local DALI for {query_structure.name}...")
        
        # Create output directory for this query
        query_output_dir = self.output_dir / output_name
        query_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run DALI
        cmd = [
            str(self.dali_cmd),
            "-query", str(query_structure),
            "-hera", str(query_output_dir),
        ]
        
        logger.debug(f"Running: {' '.join(cmd)}")
        
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            
            if process.returncode != 0:
                raise RuntimeError(
                    f"DALI failed with code {process.returncode}: {process.stderr}"
                )
            
            # Parse results
            log_file = query_output_dir / "dali.log"
            if not log_file.exists():
                # Try alternative log locations
                for pattern in ["*.log", "*-dali.txt"]:
                    logs = list(query_output_dir.glob(pattern))
                    if logs:
                        log_file = logs[0]
                        break
            
            if not log_file.exists():
                raise FileNotFoundError(f"DALI log file not found in {query_output_dir}")
            
            results = self._parse_dali_log(log_file, output_name)
            logger.info(f"Found {len(results)} alignments for {query_structure.name}")
            return results
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Local DALI timed out after {self.timeout}s")
    
    def _parse_dali_log(self, log_path: Path, query_name: str) -> List[DaliResult]:
        """
        Parse DALI log file to extract results.
        
        Expected format:
        # Rank PDB    Z    rmsd lali nres  %id  Description
        1    1ABC   45.2  1.8  234  250   25   Protein description
        """
        results = []
        
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) < 4:
                    continue
                
                try:
                    result = DaliResult(
                        query_name=query_name,
                        rank=int(parts[0]),
                        target_pdb=parts[1],
                        z_score=float(parts[2]) if len(parts) > 2 else 0.0,
                        rmsd=float(parts[3]) if len(parts) > 3 else 0.0,
                        lali=int(parts[4]) if len(parts) > 4 else None,
                        nres=int(parts[5]) if len(parts) > 5 else None,
                        identity=float(parts[6]) if len(parts) > 6 else None,
                    )
                    results.append(result)
                except (ValueError, IndexError) as e:
                    logger.debug(f"Could not parse line: {line} ({e})")
                    continue
        
        return sorted(results, key=lambda x: x.z_score, reverse=True)
    
    def _save_results(self, results: List[DaliResult], output_name: str):
        """Save results to CSV and TSV files."""
        if not results:
            logger.warning("No results to save")
            return
        
        output_path = self.output_dir / f"{output_name}_results.csv"
        
        if HAS_PANDAS:
            df = pd.DataFrame([r.to_dict() for r in results])
            df.to_csv(output_path, index=False)
            logger.info(f"Results saved to {output_path}")
        else:
            # Fallback to manual CSV writing
            with open(output_path, 'w') as f:
                # Write header
                f.write("query,target_pdb,rank,z_score,rmsd,lali,nres,identity\n")
                # Write data
                for r in results:
                    f.write(
                        f"{r.query_name},{r.target_pdb},{r.rank},"
                        f"{r.z_score},{r.rmsd},{r.lali},{r.nres},{r.identity}\n"
                    )
            logger.info(f"Results saved to {output_path}")
    
    def align_batch(
        self,
        query_structures: Iterable[Path],
        database: str = "pdb25",
        parallel: bool = False,
    ) -> List[Tuple[str, List[DaliResult]]]:
        """
        Align multiple structures in batch.
        
        Args:
            query_structures: Iterable of structure file paths
            database: Database to search against
            parallel: Whether to run in parallel (only for local mode)
            
        Returns:
            List of (query_name, results) tuples
        """
        all_results = []
        
        for query in query_structures:
            try:
                results = self.align(query, database=database)
                all_results.append((query.stem, results))
            except Exception as e:
                logger.error(f"Failed to process {query.name}: {e}")
                all_results.append((query.stem, []))
        
        return all_results
    
    def summarize_results(
        self,
        results_list: List[Tuple[str, List[DaliResult]]],
        top_n: int = 10,
    ) -> Optional['pd.DataFrame']:
        """
        Create a summary DataFrame from batch results.
        
        Args:
            results_list: List of (query_name, results) tuples
            top_n: Number of top hits to include per query
            
        Returns:
            DataFrame with all results, or None if pandas not available
        """
        if not HAS_PANDAS:
            logger.warning("pandas not available, cannot create summary DataFrame")
            return None
        
        all_data = []
        for query_name, results in results_list:
            for result in results[:top_n]:
                all_data.append(result.to_dict())
        
        if not all_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        df = df.sort_values(by='z_score', ascending=False)
        
        return df


def run_dali_alignment(
    query_structure: Path,
    mode: str = 'auto',
    database: str = 'pdb25',
    output_dir: Optional[Path] = None,
) -> List[DaliResult]:
    """
    Convenience function to run DALI alignment.
    
    Args:
        query_structure: Path to query PDB file
        mode: 'online', 'local', or 'auto'
        database: Database to search (online mode)
        output_dir: Output directory
        
    Returns:
        List of DaliResult objects
    """
    aligner = DaliAligner(mode=mode, output_dir=output_dir)
    return aligner.align(query_structure, database=database)


def batch_align(
    structures_dir: Path,
    pattern: str = "*.pdb",
    mode: str = 'auto',
    output_dir: Optional[Path] = None,
) -> List[Tuple[str, List[DaliResult]]]:
    """
    Convenience function to align all structures in a directory.
    
    Args:
        structures_dir: Directory containing structure files
        pattern: Glob pattern for structure files
        mode: 'online', 'local', or 'auto'
        output_dir: Output directory
        
    Returns:
        List of (query_name, results) tuples
    """
    if not structures_dir.exists():
        raise FileNotFoundError(f"Directory not found: {structures_dir}")
    
    structures = sorted(structures_dir.glob(pattern))
    if not structures:
        logger.warning(f"No structures found matching {pattern} in {structures_dir}")
        return []
    
    aligner = DaliAligner(mode=mode, output_dir=output_dir)
    return aligner.align_batch(structures)
