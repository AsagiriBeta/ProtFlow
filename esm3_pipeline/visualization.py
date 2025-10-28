"""
Visualization utilities for ProtFlow pipeline.
"""
from pathlib import Path
from typing import Optional, List
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from .logger import get_logger

logger = get_logger(__name__)


def plot_affinity_distribution(
    results_df: pd.DataFrame,
    output_path: Path,
    title: str = "Docking Affinity Distribution"
) -> Optional[Path]:
    """
    Plot distribution of docking affinities.

    Args:
        results_df: DataFrame with 'affinity' column
        output_path: Output image path
        title: Plot title

    Returns:
        Path to saved plot or None
    """
    if not HAS_MATPLOTLIB:
        logger.warning("Matplotlib not available, skipping plot")
        return None

    if 'affinity' not in results_df.columns:
        logger.warning("No affinity column in results")
        return None

    affinities = results_df['affinity'].dropna()

    if affinities.empty:
        logger.warning("No affinity data to plot")
        return None

    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(affinities, bins=20, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Affinity (kcal/mol)')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.axvline(affinities.mean(), color='red', linestyle='--',
                   label=f'Mean: {affinities.mean():.2f}')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Affinity plot saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create plot: {e}")
        return None


def plot_top_results(
    results_df: pd.DataFrame,
    output_path: Path,
    top_n: int = 10,
    title: str = "Top Docking Results"
) -> Optional[Path]:
    """
    Plot top N docking results as a bar chart.

    Args:
        results_df: DataFrame with 'pdb' and 'affinity' columns
        output_path: Output image path
        top_n: Number of top results to show
        title: Plot title

    Returns:
        Path to saved plot or None
    """
    if not HAS_MATPLOTLIB:
        logger.warning("Matplotlib not available, skipping plot")
        return None

    if 'affinity' not in results_df.columns or 'pdb' not in results_df.columns:
        logger.warning("Required columns missing")
        return None

    try:
        # Get top results
        top_results = results_df.nsmallest(top_n, 'affinity')

        if top_results.empty:
            logger.warning("No results to plot")
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        # Extract protein names
        proteins = [Path(p).stem for p in top_results['pdb']]
        affinities = top_results['affinity'].values

        bars = ax.barh(proteins, affinities, color='steelblue')
        ax.set_xlabel('Affinity (kcal/mol)')
        ax.set_ylabel('Protein')
        ax.set_title(title)
        ax.invert_xaxis()  # Lower affinity is better

        # Add value labels
        for bar, val in zip(bars, affinities):
            ax.text(val, bar.get_y() + bar.get_height()/2,
                   f'{val:.2f}', va='center', ha='right', fontsize=9)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Top results plot saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create plot: {e}")
        return None


def plot_pocket_scores(
    pockets_df: pd.DataFrame,
    output_path: Path,
    title: str = "Pocket Prediction Scores"
) -> Optional[Path]:
    """
    Plot pocket prediction scores.

    Args:
        pockets_df: DataFrame with 'pdb' and 'score' columns
        output_path: Output image path
        title: Plot title

    Returns:
        Path to saved plot or None
    """
    if not HAS_MATPLOTLIB:
        logger.warning("Matplotlib not available, skipping plot")
        return None

    if 'score' not in pockets_df.columns:
        logger.warning("No score column in pockets")
        return None

    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        scores = pockets_df['score']
        ax.hist(scores, bins=20, edgecolor='black', alpha=0.7, color='green')
        ax.set_xlabel('P2Rank Score')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.axvline(scores.mean(), color='red', linestyle='--',
                   label=f'Mean: {scores.mean():.2f}')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Pocket scores plot saved to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create plot: {e}")
        return None


def generate_summary_plots(
    base_dir: Path,
    pockets_csv: Optional[Path] = None,
    vina_csv: Optional[Path] = None
) -> List[Path]:
    """
    Generate all summary plots.

    Args:
        base_dir: Base directory for outputs
        pockets_csv: Path to pockets CSV
        vina_csv: Path to Vina results CSV

    Returns:
        List of generated plot paths
    """
    plots = []

    viz_dir = base_dir / 'visualizations'
    viz_dir.mkdir(exist_ok=True)

    # Pocket plots
    if pockets_csv and pockets_csv.exists():
        logger.info("Generating pocket visualizations")
        pockets_df = pd.read_csv(pockets_csv)

        plot_path = plot_pocket_scores(pockets_df, viz_dir / 'pocket_scores.png')
        if plot_path:
            plots.append(plot_path)

    # Vina plots
    if vina_csv and vina_csv.exists():
        logger.info("Generating docking visualizations")
        vina_df = pd.read_csv(vina_csv)

        plot_path = plot_affinity_distribution(vina_df, viz_dir / 'affinity_distribution.png')
        if plot_path:
            plots.append(plot_path)

        plot_path = plot_top_results(vina_df, viz_dir / 'top_results.png')
        if plot_path:
            plots.append(plot_path)

    logger.info(f"Generated {len(plots)} visualization(s)")
    return plots

