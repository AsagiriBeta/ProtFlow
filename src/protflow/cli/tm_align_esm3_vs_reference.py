"""
ESM3 预测结构 vs 参考目录（如 bf_structure）TM-align 比对

以 esm3_structures_by_sample 为查询、以参考目录（如 TPS_database/reviewed_results/bf_structure）
为目标：对每个样本内的每个 ESM3 结构与参考目录内全部 PDB 做 TM-align。
Query=ESM3 预测，Target=参考结构。

用法：
    python -m protflow.cli.tm_align_esm3_vs_reference \\
      --input ~/esm3run/predicted/esm3_structures_by_sample \\
      --reference ~/esm3run/TPS_database/reviewed_results/bf_structure \\
      --output ./tm_align_esm3_vs_bf_structure
"""
import os
import argparse
import logging
import time
from pathlib import Path

from protflow.core.structure_comparison import (
    compare_esm3_samples_vs_reference,
    plot_comparison_results,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_ESM3_SAMPLES = os.environ.get(
    "ESM3_STRUCTURES_BY_SAMPLE",
    os.path.expanduser("~/esm3run/predicted/esm3_structures_by_sample"),
)
DEFAULT_REFERENCE = os.environ.get(
    "TM_ALIGN_REFERENCE",
    os.path.expanduser("~/esm3run/TPS_database/reviewed_results/bf_structure"),
)
DEFAULT_OUTPUT = os.environ.get("TM_ALIGN_OUTPUT", "tm_align_esm3_vs_reference")


def main():
    parser = argparse.ArgumentParser(
        description="ESM3 预测结构 vs 参考目录（如 bf_structure）TM-align：每个 ESM3 对参考目录内全部 PDB 做比对",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path(DEFAULT_ESM3_SAMPLES),
        help=f"esm3_structures_by_sample 顶层目录（默认: {DEFAULT_ESM3_SAMPLES}）",
    )
    parser.add_argument(
        "--reference",
        "-r",
        type=Path,
        default=Path(DEFAULT_REFERENCE),
        help=f"参考 PDB 目录，如 bf_structure（默认: {DEFAULT_REFERENCE}）",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(DEFAULT_OUTPUT).resolve(),
        help="结果输出根目录，每个样本写入 <output>/<sample_id>/comparison_results.csv",
    )
    parser.add_argument(
        "--pattern",
        default="*.pdb",
        help="PDB 文件名通配符（默认: *.pdb）",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=None,
        help="并行进程数（默认: CPU 核心数）",
    )
    parser.add_argument(
        "--write-batch-size",
        type=int,
        default=10000,
        help="每批写入条数（默认: 10000）",
    )
    parser.add_argument(
        "--no-collect-results",
        action="store_true",
        help="不收集全部结果到内存，仅写 CSV（大批量时建议使用）",
    )
    parser.add_argument(
        "--min-pdbs",
        type=int,
        default=1,
        help="样本内至少有多少个 PDB 才参与比对（默认: 1）",
    )
    parser.add_argument(
        "--sample",
        action="append",
        dest="samples",
        metavar="SAMPLE_ID",
        help="仅处理指定样本目录（可多次指定）；不指定则处理全部子目录",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="对每个样本生成 comparison_plot.png（样本内结果较多时可能较慢）",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="断点续跑：跳过已有 (Query,Target) 对，只跑未完成的任务并追加写入",
    )
    args = parser.parse_args()

    input_dir = args.input.resolve()
    reference_dir = args.reference.resolve()
    output_dir = args.output.resolve()

    if not input_dir.exists():
        logger.error("输入目录不存在: %s", input_dir)
        return 1
    if not reference_dir.exists():
        logger.error("参考目录不存在: %s", reference_dir)
        logger.info("请设置 --reference 或环境变量 TM_ALIGN_REFERENCE（如 bf_structure 路径）")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("输入(ESM3): %s", input_dir)
    logger.info("参考目录: %s", reference_dir)
    logger.info("输出: %s", output_dir)

    t0 = time.perf_counter()
    results_by_sample = compare_esm3_samples_vs_reference(
        parent_dir=input_dir,
        reference_dir=reference_dir,
        output_base=output_dir,
        pattern=args.pattern,
        num_workers=args.num_workers,
        write_batch_size=args.write_batch_size,
        collect_results=not args.no_collect_results,
        sample_dirs=args.samples,
        min_pdbs=args.min_pdbs,
        resume=args.resume,
    )
    elapsed = time.perf_counter() - t0
    total_pairs = sum(len(r) for r in results_by_sample.values())
    logger.info(
        "完成。共处理 %d 个样本，%d 对比对，总耗时 %.1fs，平均 %.1f 对/s",
        len(results_by_sample),
        total_pairs,
        elapsed,
        total_pairs / elapsed if elapsed > 0 else 0,
    )

    if args.plot and not args.no_collect_results:
        for sample_id, results in results_by_sample.items():
            if not results:
                continue
            plot_path = output_dir / sample_id / "comparison_plot.png"
            plot_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                plot_comparison_results(
                    results=results,
                    output_path=plot_path,
                    title=sample_id,
                )
            except Exception as e:
                logger.warning("绘制 %s 失败: %s", sample_id, e)

    logger.info("结果见 %s", output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
