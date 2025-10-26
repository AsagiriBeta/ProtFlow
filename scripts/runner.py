#!/usr/bin/env python3
"""
CLI runner to execute selected steps of the pipeline.
Examples:
  python -m scripts.runner --parse-gbk --predict --p2rank --vina --report \
      --gbk-dir ./esm3_pipeline/gbk_input --smiles "CCO" --limit 5

Each step is optional; missing tools are skipped gracefully.
"""
from pathlib import Path
import argparse
import sys
import pandas as pd

from esm3_pipeline import BASE, GBK_DIR, PDB_DIR
from esm3_pipeline.seq_parser import extract_proteins_from_gbk, filter_and_select
from esm3_pipeline.esm3_predict import load_esm3_small, predict_pdbs
from esm3_pipeline.p2rank import ensure_p2rank, run_p2rank_on_pdbs
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt
from esm3_pipeline.vina_dock import run_vina
from esm3_pipeline.antismash import run_antismash, is_antismash_available


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description='ESM3-sm pipeline runner')
    ap.add_argument('--gbk-dir', type=Path, default=GBK_DIR)
    ap.add_argument('--base', type=Path, default=BASE)
    ap.add_argument('--limit', type=int, default=10)
    ap.add_argument('--min-len', type=int, default=50)
    ap.add_argument('--max-len', type=int, default=1200)

    ap.add_argument('--parse-gbk', action='store_true')
    ap.add_argument('--predict', action='store_true')
    ap.add_argument('--p2rank', action='store_true')
    ap.add_argument('--vina', action='store_true')
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--antismash', action='store_true')

    ap.add_argument('--smiles', type=str, default='')
    ap.add_argument('--ligand', type=Path)

    args = ap.parse_args(argv)

    base = args.base
    gbk_dir = args.gbk_dir
    pdb_dir = PDB_DIR

    base.mkdir(parents=True, exist_ok=True)
    gbk_dir.mkdir(parents=True, exist_ok=True)
    pdb_dir.mkdir(parents=True, exist_ok=True)

    fasta_all = base / 'all_proteins.faa'
    selected_fasta = base / 'selected.faa'

    # Step: parse GBK
    if args.parse_gbk:
        n = extract_proteins_from_gbk(gbk_dir, fasta_all)
        print(f'Parsed {n} protein sequences -> {fasta_all}')
        if n == 0:
            print('No sequences found. Provide FASTA manually if needed.', file=sys.stderr)

    # Step: filter and select
    if args.predict or args.p2rank or args.vina or args.report:
        selected = filter_and_select(fasta_all, args.min_len, args.max_len, args.limit, selected_fasta)
        print(f'Selected {len(selected)} sequences -> {selected_fasta}')

    # Step: predict with ESM3-sm
    if args.predict:
        model, device = load_esm3_small()
        from Bio import SeqIO
        seqs = list(SeqIO.parse(str(selected_fasta), 'fasta'))
        if not seqs:
            print('No sequences to predict. Did you run --parse-gbk?', file=sys.stderr)
        else:
            predict_pdbs(model, seqs, pdb_dir)
            print(f'Wrote PDBs to {pdb_dir}')

    # Step: P2Rank
    pockets_df = None
    if args.p2rank:
        p2jar = ensure_p2rank(base)
        if p2jar is None:
            print('P2Rank not available; skipping', file=sys.stderr)
        else:
            results = run_p2rank_on_pdbs(p2jar, pdb_dir)
            pockets_df = pd.DataFrame(results)
            if not pockets_df.empty:
                pockets_df.to_csv(base / 'pockets_summary.csv', index=False)
            print('P2Rank done')

    # Step: ligand prep and Vina
    if args.vina:
        if pockets_df is None:
            pock_file = base / 'pockets_summary.csv'
            if pock_file.exists():
                pockets_df = pd.read_csv(pock_file)
            else:
                pockets_df = pd.DataFrame()
        ligand_pdbqt = None
        if args.ligand:
            ligand_pdbqt = smiles_or_file_to_pdbqt(str(args.ligand), base)
        elif args.smiles:
            ligand_pdbqt = smiles_or_file_to_pdbqt(args.smiles, base)
        if ligand_pdbqt and not pockets_df.empty:
            dfg = run_vina(ligand_pdbqt, pockets_df, base)
            dfg.to_csv(base / 'vina_results.csv', index=False)
            print('Vina docking complete')
        else:
            print('Skipping Vina: missing ligand or pockets')

    # Step: antiSMASH
    if args.antismash:
        if not is_antismash_available():
            print('antiSMASH is not installed; skipping', file=sys.stderr)
        else:
            # Prefer a single GBK input; fallback to any in gbk_dir
            gbks = list(gbk_dir.glob('*.gbk')) + list(gbk_dir.glob('*.gbff'))
            if not gbks:
                print('No GBK/GBFF files found for antiSMASH', file=sys.stderr)
            else:
                out_as = base / 'antismash_out'
                res = run_antismash(gbks[0], out_as)
                print(f'antiSMASH results at: {res}')

    # Step: report
    if args.report:
        from esm3_pipeline.reporting import build_report
        build_report(base, pdb_dir, base / 'esm3_results_report.pdf')
        print('Report generated')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
