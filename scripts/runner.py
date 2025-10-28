#!/usr/bin/env python3
"""
CLI runner to execute selected steps of the pipeline.

Examples:
  # Run full pipeline
  python -m scripts.runner --parse-gbk --predict --p2rank --vina --report \
      --gbk-dir ./esm3_pipeline/gbk_input --smiles "CCO" --limit 5

  # Just parse and predict
  python -m scripts.runner --parse-gbk --predict --limit 10

  # Use config file
  python -m scripts.runner --config protflow_config.json --predict --report

Each step is optional; missing tools are skipped gracefully.
"""
from pathlib import Path
import argparse
import sys
import pandas as pd
from typing import Optional

from esm3_pipeline import BASE, GBK_DIR, PDB_DIR
from esm3_pipeline.config import ProtFlowConfig, set_config
from esm3_pipeline.logger import setup_logging, get_logger
from esm3_pipeline.exceptions import ProtFlowError
from esm3_pipeline.seq_parser import extract_proteins_from_gbk, filter_and_select
from esm3_pipeline.esm3_predict import load_esm3_small, predict_pdbs, clear_model_cache
from esm3_pipeline.p2rank import ensure_p2rank, run_p2rank_on_pdbs
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt
from esm3_pipeline.vina_dock import run_vina


def main(argv=None) -> int:
    """Main entry point for the CLI runner."""
    ap = argparse.ArgumentParser(
        description='ProtFlow pipeline runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Configuration
    ap.add_argument('--config', type=Path, help='Path to configuration file (JSON/YAML)')
    ap.add_argument('--gbk-dir', type=Path, default=GBK_DIR, help='GenBank files directory')
    ap.add_argument('--base', type=Path, default=BASE, help='Base output directory')

    # Sequence filtering
    ap.add_argument('--limit', type=int, default=10, help='Max sequences to process')
    ap.add_argument('--min-len', type=int, default=50, help='Minimum sequence length')
    ap.add_argument('--max-len', type=int, default=1200, help='Maximum sequence length')

    # Pipeline steps
    ap.add_argument('--parse-gbk', action='store_true', help='Parse GenBank files')
    ap.add_argument('--predict', action='store_true', help='Run ESM3 structure prediction')
    ap.add_argument('--p2rank', action='store_true', help='Run P2Rank pocket detection')
    ap.add_argument('--vina', action='store_true', help='Run Vina docking')
    ap.add_argument('--report', action='store_true', help='Generate PDF report')

    # Ligand options
    ap.add_argument('--smiles', type=str, default='', help='Ligand SMILES string')
    ap.add_argument('--ligand', type=Path, help='Path to ligand file')

    # Performance options
    ap.add_argument('--parallel', action='store_true', help='Enable parallel processing')
    ap.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    ap.add_argument('--no-cache', action='store_true', help='Disable caching')

    # Logging
    ap.add_argument('--log-level', default='INFO',
                   choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                   help='Logging level')
    ap.add_argument('--log-file', type=Path, help='Path to log file')
    ap.add_argument('--quiet', action='store_true', help='Suppress console output')

    args = ap.parse_args(argv)

    # Setup logging
    logger = setup_logging(
        level=args.log_level,
        log_file=args.log_file,
        console=not args.quiet
    )

    logger.info("=" * 60)
    logger.info("ProtFlow Pipeline Runner v0.2.0")
    logger.info("=" * 60)

    try:
        # Load configuration
        if args.config:
            logger.info(f"Loading configuration from {args.config}")
            config = ProtFlowConfig.from_file(args.config)
        else:
            config = ProtFlowConfig()

        # Override with command line arguments
        if args.base != BASE:
            config.base_dir = args.base
        if args.gbk_dir != GBK_DIR:
            config.gbk_dir = args.gbk_dir

        config.min_seq_length = args.min_len
        config.max_seq_length = args.max_len
        config.max_sequences = args.limit
        config.enable_cache = not args.no_cache
        config.max_workers = args.workers

        set_config(config)

        # Setup paths
        base = config.base_dir
        gbk_dir = config.gbk_dir
        pdb_dir = config.pdb_dir

        base.mkdir(parents=True, exist_ok=True)
        gbk_dir.mkdir(parents=True, exist_ok=True)
        pdb_dir.mkdir(parents=True, exist_ok=True)

        fasta_all = base / 'all_proteins.faa'
        selected_fasta = base / 'selected.faa'

        # Step: parse GBK
        if args.parse_gbk:
            logger.info("Step 1: Parsing GenBank files")
            n = extract_proteins_from_gbk(gbk_dir, fasta_all)
            if n == 0:
                logger.warning('No sequences found. Provide FASTA manually if needed.')
            else:
                logger.info(f"✓ Extracted {n} protein sequences")

        # Step: filter and select
        if args.predict or args.p2rank or args.vina or args.report:
            if not fasta_all.exists():
                logger.error(f"FASTA file not found: {fasta_all}")
                return 1

            logger.info("Step 2: Filtering sequences")
            selected = filter_and_select(
                fasta_all,
                config.min_seq_length,
                config.max_seq_length,
                config.max_sequences,
                selected_fasta
            )
            logger.info(f"✓ Selected {len(selected)} sequences")

        # Step: predict with ESM3-sm
        if args.predict:
            logger.info("Step 3: Predicting structures with ESM3")
            model, device = load_esm3_small(use_cache=config.enable_cache)

            from Bio import SeqIO
            seqs = list(SeqIO.parse(str(selected_fasta), 'fasta'))
            if not seqs:
                logger.error('No sequences to predict. Did you run --parse-gbk?')
                return 1

            predict_pdbs(
                model, seqs, pdb_dir,
                num_steps=config.esm3_num_steps,
                show_progress=not args.quiet,
                cache_predictions=config.enable_cache
            )
            logger.info(f"✓ Predicted {len(seqs)} structures")

            # Clear model from memory if not caching
            if not config.enable_cache:
                clear_model_cache()

        # Step: P2Rank
        pockets_df = None
        if args.p2rank:
            logger.info("Step 4: Running P2Rank pocket detection")
            try:
                p2jar = ensure_p2rank(base, version=config.p2rank_version)
                if p2jar is None:
                    logger.error('P2Rank installation failed')
                else:
                    results = run_p2rank_on_pdbs(
                        p2jar, pdb_dir,
                        threads=config.p2rank_threads,
                        visualizations=config.p2rank_visualizations
                    )
                    pockets_df = pd.DataFrame(results)
                    if not pockets_df.empty:
                        pockets_csv = base / 'pockets_summary.csv'
                        pockets_df.to_csv(pockets_csv, index=False)
                        logger.info(f"✓ Detected {len(pockets_df)} pockets")
                    else:
                        logger.warning("No pockets detected")
            except Exception as e:
                logger.error(f"P2Rank failed: {e}")

        # Step: ligand prep and Vina
        if args.vina:
            logger.info("Step 5: Running Vina docking")

            # Load pockets if not already loaded
            if pockets_df is None:
                pock_file = base / 'pockets_summary.csv'
                if pock_file.exists():
                    pockets_df = pd.read_csv(pock_file)
                else:
                    pockets_df = pd.DataFrame()

            if pockets_df.empty:
                logger.error('No pockets available for docking')
            else:
                # Prepare ligand
                ligand_pdbqt = None
                if args.ligand:
                    ligand_pdbqt = smiles_or_file_to_pdbqt(str(args.ligand), base)
                elif args.smiles:
                    ligand_pdbqt = smiles_or_file_to_pdbqt(args.smiles, base)

                if ligand_pdbqt:
                    dfg = run_vina(
                        ligand_pdbqt, pockets_df, base,
                        box_size=config.vina_box_size,
                        exhaustiveness=config.vina_exhaustiveness,
                        num_modes=config.vina_num_modes,
                        parallel=args.parallel,
                        max_workers=config.max_workers
                    )
                    vina_csv = base / 'vina_results.csv'
                    dfg.to_csv(vina_csv, index=False)
                    logger.info(f"✓ Docking complete, results saved to {vina_csv}")
                else:
                    logger.error('No ligand provided for docking')

        # Step: report
        if args.report:
            logger.info("Step 6: Generating report")
            from esm3_pipeline.reporting import build_report
            report_path = base / 'esm3_results_report.pdf'
            build_report(base, pdb_dir, report_path)
            logger.info(f"✓ Report generated: {report_path}")

        logger.info("=" * 60)
        logger.info("Pipeline completed successfully!")
        logger.info("=" * 60)
        return 0

    except ProtFlowError as e:
        logger.error(f"Pipeline error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

