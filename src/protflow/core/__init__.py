"""Core functionality for ProtFlow pipeline."""

from .antismash import *
from .cds_comparison import *
try:
    from .reporting import *
except ImportError:
    # reportlab 未安装时 reporting 不可用，仅用 TM-align 等可不装 reportlab
    build_report = None
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
    batch_compare_tm_align_from_dir,
    batch_compare_tm_align_from_sample_dirs,
    compare_esm3_samples_vs_reference,
    run_tm_align_esm3_samples,
    compare_against_reference,
    compare_structures_pairwise,
    plot_comparison_results,
    ComparisonResult,
)
from .tm_align_db import (
    get_connection,
    create_schema,
    import_csv_to_db,
    import_from_sample_dir,
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
    "batch_compare_tm_align_from_dir",
    "batch_compare_tm_align_from_sample_dirs",
    "compare_esm3_samples_vs_reference",
    "run_tm_align_esm3_samples",
    "compare_against_reference",
    "compare_structures_pairwise",
    "plot_comparison_results",
    "ComparisonResult",
    "get_connection",
    "create_schema",
    "import_csv_to_db",
    "import_from_sample_dir",
]