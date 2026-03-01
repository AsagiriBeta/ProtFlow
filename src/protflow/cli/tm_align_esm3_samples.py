"""
以 esm3_structures_by_sample 为输入的 TM-align 批量比对

目录结构：
    esm3_structures_by_sample/
        1001240_GCF_014200405.1/
            CHDELLME_00003.pdb
            CHDELLME_01426.pdb
            ...
        2582905_GCF_005954645.2/
            *.pdb
        ...

对每个样本子目录内的 PDB 做两两 TM-align，结果写入 output_base/<sample_id>/comparison_results.csv。

用法：
    python -m protflow.cli.tm_align_esm3_samples --input /path/to/esm3_structures_by_sample --output ./outputs/tm_align_by_sample
    或设置环境变量后：
    export ESM3_STRUCTURES_BY_SAMPLE=/path/to/esm3_structures_by_sample
    python -m protflow.cli.tm_align_esm3_samples
"""
import os
import argparse
import logging
import time
from pathlib import Path

from protflow.core.structure_comparison import (
    batch_compare_tm_align_from_sample_dirs,
    plot_comparison_results,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 默认路径：可与 esm3run 联合使用
DEFAULT_ESM3_SAMPLES = os.environ.get(
    "ESM3_STRUCTURES_BY_SAMPLE",
    os.path.expanduser("~/esm3run/predicted/esm3_structures_by_sample"),
)
DEFAULT_OUTPUT = os.environ.get("TM_ALIGN_OUTPUT", "outputs/tm_align_by_sample")


def main():
    parser = argparse.ArgumentParser(
        description="以 esm3_structures_by_sample 为输入，按样本目录批量 TM-align 比对",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path(DEFAULT_ESM3_SAMPLES),
        help=f"esm3_structures_by_sample 顶层目录（默认: {DEFAULT_ESM3_SAMPLES} 或环境变量 ESM3_STRUCTURES_BY_SAMPLE）",
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
    output_dir = args.output.resolve()

    if not input_dir.exists():
        logger.error("输入目录不存在: %s", input_dir)
        logger.info("请设置 --input 或环境变量 ESM3_STRUCTURES_BY_SAMPLE")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("输入: %s", input_dir)
    logger.info("输出: %s", output_dir)

    t0 = time.perf_counter()
    results_by_sample = batch_compare_tm_align_from_sample_dirs(
        parent_dir=input_dir,
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
    logger.info("完成。共处理 %d 个样本，%d 对比对，总耗时 %.1fs，平均 %.1f 对/s", 
                len(results_by_sample), total_pairs, elapsed, total_pairs / elapsed if elapsed > 0 else 0)

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
