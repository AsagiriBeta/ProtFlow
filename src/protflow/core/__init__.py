"""Core functionality for ProtFlow pipeline."""

from .antismash import *
from .cds_comparison import *
from .reporting import *
from .pipeline import ProkkaESM3Pipeline
from .structure_analysis import (
    collect_structure_files,
    assess_structure_quality,
    batch_quality_assessment,
    calculate_structure_similarity,
    batch_similarity_analysis,
    perform_clustering_analysis,
    generate_comprehensive_report,
)
from .structure_comparison import (
    compare_structures_tm_align,
    batch_compare_tm_align,
    compare_against_reference,
    compare_structures_pairwise,
    plot_comparison_results,
    ComparisonResult,
)

__all__ = [
    "run_antismash",
    "compare_cds_annotations",
    "generate_report",
    "ReportGenerator",
    "ProkkaESM3Pipeline",
    "collect_structure_files",
    "assess_structure_quality",
    "batch_quality_assessment",
    "calculate_structure_similarity",
    "batch_similarity_analysis",
    "perform_clustering_analysis",
    "generate_comprehensive_report",
    "compare_structures_tm_align",
    "batch_compare_tm_align",
    "compare_against_reference",
    "compare_structures_pairwise",
    "plot_comparison_results",
    "ComparisonResult",
]