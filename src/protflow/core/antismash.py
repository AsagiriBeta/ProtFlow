from pathlib import Path
import subprocess
from typing import Optional, List
import shutil
import os

"""
Lightweight antiSMASH runner.
- Prefers a local antiSMASH install (via conda/pip) if available.
- Falls back to the official Docker wrapper `run_antismash` if present in PATH.
- Also supports running via a conda environment without switching kernels:
  set ANTISMASH_ENV (default 'antismash') and it will use `conda run -n <env> antismash`.
- Accepts a GenBank file (.gbk/.gbff) or FASTA nucleotide file as input.
- Writes outputs into a specified directory.

This is optional and can be skipped if antiSMASH isn't available.
"""


def _find_antismash_runner() -> Optional[List[str]]:
    """Return a command prefix list to run antiSMASH, if available.
    Tries in order:
      1) native 'antismash' on PATH
      2) Docker wrapper 'run_antismash' on PATH
      3) conda environment (ANTISMASH_ENV, default 'antismash') via `conda run -n`
    Returns the command prefix list, e.g., ['antismash'] or ['run_antismash'] or ['conda','run','-n','antismash','antismash'].
    """
    # 1) native
    exe = shutil.which('antismash')
    if exe:
        return ['antismash']

    # 2) docker wrapper
    exe = shutil.which('run_antismash')
    if exe:
        return ['run_antismash']

    # 3) conda env
    env_name = os.getenv('ANTISMASH_ENV', 'antismash')
    conda_exe = shutil.which('conda') or shutil.which('mamba') or shutil.which('micromamba')
    if conda_exe:
        probe = [conda_exe, 'run', '-n', env_name, 'antismash', '--help']
        try:
            res = subprocess.run(probe, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                return [conda_exe, 'run', '-n', env_name, 'antismash']
        except Exception:
            pass

    return None


def get_runner() -> Optional[List[str]]:
    """Expose the runner for UI code; returns the command prefix list or None."""
    return _find_antismash_runner()


def is_antismash_available() -> bool:
    runner = _find_antismash_runner()
    if not runner:
        return False
    try:
        # All variants support --help (native, conda-run, docker wrapper)
        subprocess.run(runner + ['--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def run_antismash(input_path: Path, out_dir: Path, extra_args: Optional[List[str]] = None) -> Optional[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    runner = _find_antismash_runner()
    if not runner:
        return None

    # Ensure absolute paths
    inp_abs = str(input_path.resolve())
    out_abs = str(out_dir.resolve())

    # Build command depending on runner flavor
    if runner and runner[0] == 'run_antismash':
        # Docker wrapper semantics: input then output dir (positional)
        args = runner + [inp_abs, out_abs]
    else:
        # Native or conda-run semantics: input then --output-dir <dir>
        args = runner + [inp_abs, '--output-dir', out_abs]

    if extra_args:
        args.extend(extra_args)

    subprocess.run(args)

    index_html = Path(out_abs) / 'index.html'
    return index_html if index_html.exists() else Path(out_abs)
