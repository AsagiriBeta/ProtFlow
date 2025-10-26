from pathlib import Path
from typing import List
from Bio import SeqIO


def extract_proteins_from_gbk(gbk_dir: Path, out_fasta: Path) -> int:
    """
    Parse all .gbk/.gbff files under gbk_dir and write protein translations to FASTA.
    Returns number of sequences written.
    """
    count = 0
    with open(out_fasta, 'w') as outf:
        for fn in sorted(gbk_dir.glob('**/*.gbk')) + sorted(gbk_dir.glob('**/*.gbff')):
            for rec in SeqIO.parse(str(fn), 'genbank'):
                for feat in rec.features:
                    if feat.type == 'CDS':
                        q = feat.qualifiers
                        prot = q.get('translation', [''])[0]
                        if prot:
                            gene = q.get('gene', ['unknown'])[0]
                            pid = q.get('protein_id', [''])[0]
                            header = f'>{rec.id}|{fn.name}|{pid}|{gene}\n'
                            outf.write(header)
                            outf.write(prot + '\n')
                            count += 1
    return count


def filter_and_select(fasta: Path, min_len: int = 50, max_len: int = 1200, limit: int = 10, out_fasta: Path = None) -> List[SeqIO.SeqRecord]:
    records = list(SeqIO.parse(str(fasta), 'fasta'))
    filtered = [r for r in records if min_len <= len(r.seq) <= max_len]
    selected = filtered[:limit]
    if out_fasta is not None:
        SeqIO.write(selected, str(out_fasta), 'fasta')
    return selected

