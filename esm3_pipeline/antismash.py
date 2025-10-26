from pathlib import Path
import subprocess
from typing import Optional, List
import shutil

"""
Lightweight antiSMASH runner.
- Prefers a local antiSMASH install (via conda/pip) if available.
- Falls back to the official Docker wrapper `run_antismash` if present in PATH.
- Accepts a GenBank file (.gbk/.gbff) or FASTA nucleotide file as input.
- Writes outputs into a specified directory.

This is optional and can be skipped if antiSMASH isn't available.
"""


def _find_antismash_executable() -> Optional[str]:
    """Return the executable to run: 'antismash' or 'run_antismash', otherwise None."""
    exe = shutil.which('antismash')
    if exe:
        return 'antismash'
    exe = shutil.which('run_antismash')
    if exe:
        return 'run_antismash'
    return None


def is_antismash_available() -> bool:
    exe = _find_antismash_executable()
    if not exe:
        return False
    try:
        # Prefer a quick help probe; wrapper and native both support --help
        subprocess.run([exe, '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def run_antismash(input_path: Path, out_dir: Path, extra_args: Optional[List[str]] = None) -> Optional[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    exe = _find_antismash_executable()
    if not exe:
        return None

    # Ensure absolute paths when using the Docker wrapper (required by upstream script)
    inp_abs = str(input_path.resolve())
    out_abs = str(out_dir.resolve())

    args = [exe]
    # Both native and wrapper use input first, then output dir semantics.
    # Native antiSMASH expects --output-dir <dir>, while Docker wrapper expects the dir as a positional arg.
    if exe == 'antismash':
        args.extend([inp_abs, '--output-dir', out_abs])
    else:  # run_antismash (Docker wrapper)
        args.extend([inp_abs, out_abs])

    if extra_args:
        args.extend(extra_args)

    subprocess.run(args)

    # antiSMASH typically creates index.html in out_dir; wrapper places results there as well
    index_html = Path(out_abs) / 'index.html'
    return index_html if index_html.exists() else Path(out_abs)
