"""
GenBank file parsing and sequence filtering utilities.
"""
from pathlib import Path
from typing import List, Optional, Set
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from .logger import get_logger
from .exceptions import ParseError

logger = get_logger(__name__)


def extract_proteins_from_gbk(
    gbk_dir: Path,
    out_fasta: Path,
    recursive: bool = True,
    deduplicate: bool = True
) -> int:
    """
    Parse all .gbk/.gbff files and extract protein translations to FASTA.

    Args:
        gbk_dir: Directory containing GenBank files
        out_fasta: Output FASTA file path
        recursive: Whether to search recursively
        deduplicate: Remove duplicate sequences

    Returns:
        Number of sequences written

    Raises:
        ParseError: If parsing fails
        FileNotFoundError: If gbk_dir doesn't exist
    """
    if not gbk_dir.exists():
        raise FileNotFoundError(f"GenBank directory not found: {gbk_dir}")

    logger.info(f"Parsing GenBank files from {gbk_dir}")

    count = 0
    seen_seqs: Set[str] = set() if deduplicate else None

    try:
        with open(out_fasta, 'w') as outf:
            pattern = '**/*.gbk' if recursive else '*.gbk'
            gbk_files = list(gbk_dir.glob(pattern)) + list(gbk_dir.glob(pattern.replace('.gbk', '.gbff')))

            if not gbk_files:
                logger.warning(f"No GenBank files found in {gbk_dir}")
                return 0

            logger.info(f"Found {len(gbk_files)} GenBank files")

            for fn in sorted(gbk_files):
                try:
                    for rec in SeqIO.parse(str(fn), 'genbank'):
                        for feat in rec.features:
                            if feat.type == 'CDS':
                                q = feat.qualifiers
                                prot = q.get('translation', [''])[0]
                                if prot:
                                    # Skip duplicates if requested
                                    if deduplicate:
                                        if prot in seen_seqs:
                                            continue
                                        seen_seqs.add(prot)

                                    gene = q.get('gene', ['unknown'])[0]
                                    pid = q.get('protein_id', [''])[0]
                                    locus_tag = q.get('locus_tag', [''])[0]
                                    product = q.get('product', [''])[0]

                                    # Enhanced header with more information
                                    header = f'>{rec.id}|{fn.name}|{pid}|{gene}|{locus_tag}|{product}\n'
                                    outf.write(header)
                                    outf.write(prot + '\n')
                                    count += 1
                except Exception as e:
                    logger.error(f"Failed to parse {fn}: {e}")
                    continue

        logger.info(f"Extracted {count} protein sequences to {out_fasta}")
        return count

    except Exception as e:
        raise ParseError(f"Failed to extract proteins: {e}") from e


def filter_and_select(
    fasta: Path,
    min_len: int = 50,
    max_len: int = 1200,
    limit: int = 10,
    out_fasta: Optional[Path] = None,
    sort_by_length: bool = False
) -> List[SeqRecord]:
    """
    Filter sequences by length and select a subset.

    Args:
        fasta: Input FASTA file
        min_len: Minimum sequence length
        max_len: Maximum sequence length
        limit: Maximum number of sequences to select
        out_fasta: Optional output FASTA file
        sort_by_length: Sort by length before selecting

    Returns:
        List of selected SeqRecord objects

    Raises:
        FileNotFoundError: If input FASTA doesn't exist
        ParseError: If parsing fails
    """
    if not fasta.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta}")

    logger.info(f"Filtering sequences from {fasta}")
    logger.info(f"Filters: {min_len} <= length <= {max_len}, limit={limit}")

    try:
        records = list(SeqIO.parse(str(fasta), 'fasta'))
        logger.info(f"Read {len(records)} total sequences")

        # Filter by length
        filtered = [r for r in records if min_len <= len(r.seq) <= max_len]
        logger.info(f"After length filter: {len(filtered)} sequences")

        # Sort if requested
        if sort_by_length:
            filtered.sort(key=lambda r: len(r.seq), reverse=True)
            logger.debug("Sorted sequences by length (descending)")

        # Select subset
        selected = filtered[:limit]
        logger.info(f"Selected {len(selected)} sequences")

        # Write output if requested
        if out_fasta is not None:
            SeqIO.write(selected, str(out_fasta), 'fasta')
            logger.info(f"Wrote selected sequences to {out_fasta}")

        return selected

    except Exception as e:
        raise ParseError(f"Failed to filter sequences: {e}") from e


def validate_sequence(seq: str) -> bool:
    """
    Validate that a sequence contains only valid amino acid characters.

    Args:
        seq: Protein sequence string

    Returns:
        True if valid, False otherwise
    """
    valid_aa = set('ACDEFGHIKLMNPQRSTVWY*X')
    return all(c.upper() in valid_aa for c in seq)


