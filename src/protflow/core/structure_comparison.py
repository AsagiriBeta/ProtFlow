"""
结构比对工具模块 - 支持TM-align和DALI比对

提供批量结构比对功能，支持：
- TM-align比对（使用tmtools）
- DALI比对（使用protflow.prediction.dali）
- 批量处理和结果汇总
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union, Iterator
from dataclasses import dataclass
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import logging

logger = logging.getLogger(__name__)

try:
    from tmtools import tm_align
    from tmtools.io import get_structure, get_residue_data
    TMTools_AVAILABLE = True
except ImportError:
    TMTools_AVAILABLE = False
    logger.warning("tmtools not available. TM-align comparison will not work.")


@dataclass
class ComparisonResult:
    """结构比对结果"""
    query_name: str
    target_name: str
    rmsd: float
    tm_score: float
    alignment_length: Optional[int] = None
    sequence_identity: Optional[float] = None


def compare_structures_tm_align(
    query_pdb: Path,
    target_pdb: Path,
    query_name: Optional[str] = None,
    target_name: Optional[str] = None
) -> Optional[ComparisonResult]:
    """
    使用TM-align比较两个结构
    
    Args:
        query_pdb: 查询结构PDB文件路径
        target_pdb: 目标结构PDB文件路径
        query_name: 查询结构名称（默认使用文件名）
        target_name: 目标结构名称（默认使用文件名）
    
    Returns:
        ComparisonResult对象，如果失败返回None
    """
    if not TMTools_AVAILABLE:
        logger.error("tmtools not available. Install with: pip install tmtools")
        return None
    
    try:
        s1 = get_structure(str(query_pdb))
        s2 = get_structure(str(target_pdb))
        
        chain1 = next(s1.get_chains())
        chain2 = next(s2.get_chains())
        
        coords1, seq1 = get_residue_data(chain1)
        coords2, seq2 = get_residue_data(chain2)
        
        result = tm_align(coords1, coords2, seq1, seq2)
        mean_tm = (result.tm_norm_chain1 + result.tm_norm_chain2) / 2
        
        query_name = query_name or query_pdb.stem
        target_name = target_name or target_pdb.stem
        
        return ComparisonResult(
            query_name=query_name,
            target_name=target_name,
            rmsd=result.rmsd,
            tm_score=mean_tm,
            alignment_length=result.alignment_length if hasattr(result, 'alignment_length') else None
        )
    except Exception as e:
        logger.error(f"TM-align comparison failed for {query_pdb} vs {target_pdb}: {e}")
        return None


def _worker_compare_tm_align(task: Tuple) -> Optional[ComparisonResult]:
    """供 multiprocessing.Pool 调用的模块级 worker（必须为顶层函数以便 pickle）。"""
    query_pdb, target_pdb, query_name, target_name = task
    return compare_structures_tm_align(query_pdb, target_pdb, query_name, target_name)


def _load_done_pairs_from_csv(csv_path: Path) -> set:
    """从已有 comparison_results.csv 读取已完成的 (query_name, target_name) 对。"""
    done = set()
    if not csv_path.exists():
        return done
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[0].strip() and row[1].strip():
                    done.add((row[0].strip(), row[1].strip()))
    except Exception as e:
        logger.warning(f"Could not read existing CSV for resume: {e}")
    return done


def batch_compare_tm_align(
    query_structures: List[Path],
    target_structures: List[Path],
    output_dir: Path,
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    query_names: Optional[List[str]] = None,
    target_names: Optional[List[str]] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
    resume: bool = False,
) -> List[ComparisonResult]:
    """
    批量使用 TM-align 比较结构（多进程并行，适合高通量）。

    使用 multiprocessing.Pool 进行多进程并行，每个进程独立读 PDB 并做比对，
    适合 CPU 密集型；大批量时建议配合 write_batch_size 与 collect_results 降低 IO 与内存。

    Args:
        query_structures: 查询结构 PDB 文件列表
        target_structures: 目标结构 PDB 文件列表
        output_dir: 输出目录
        num_workers: 并行进程数，默认 cpu_count() 以充分利用多核
        chunk_size: 每进程任务块大小，默认根据任务数与 num_workers 动态计算
        query_names: 查询结构名称列表（可选）
        target_names: 目标结构名称列表（可选）
        write_batch_size: 每写满多少条结果就刷新到磁盘，减少 IO 阻塞与内存；0 表示全部算完再写
        collect_results: 是否在内存中收集全部结果；大批量（如百万级）建议 False 仅写文件
        resume: 若为 True 且 output_dir/comparison_results.csv 已存在，则跳过已有 (Query,Target) 对，只跑剩余任务并追加写入

    Returns:
        比对结果列表（当 collect_results=False 时为空列表；resume 时仅含本次新产生的结果）
    """
    if not TMTools_AVAILABLE:
        logger.error("tmtools not available. Install with: pip install tmtools")
        return []

    n_cpu = cpu_count() or 4
    # 默认使用全部逻辑核心，多核服务器可充分跑满
    num_workers = num_workers if num_workers is not None else n_cpu
    output_dir.mkdir(parents=True, exist_ok=True)

    # 准备任务
    tasks = []
    for i, query_pdb in enumerate(query_structures):
        for j, target_pdb in enumerate(target_structures):
            query_name = query_names[i] if query_names and i < len(query_names) else query_pdb.stem
            target_name = target_names[j] if target_names and j < len(target_names) else target_pdb.stem
            tasks.append((query_pdb, target_pdb, query_name, target_name))

    csv_path = output_dir / "comparison_results.csv"
    done_pairs: set = set()
    if resume and csv_path.exists():
        done_pairs = _load_done_pairs_from_csv(csv_path)
        tasks = [t for t in tasks if (t[2], t[3]) not in done_pairs]
        if done_pairs:
            logger.info(f"Resume: skip {len(done_pairs)} done pairs, {len(tasks)} remaining")

    n_tasks = len(tasks)
    if n_tasks == 0:
        logger.warning("No tasks to run (all already done when resume=True)")
        return []

    if chunk_size is None:
        chunk_size = max(1, min(50, n_tasks // (num_workers * 4)))

    results: List[ComparisonResult] = []
    batch: List[ComparisonResult] = []
    total_written = 0
    file_exists = resume and csv_path.exists()
    mode = "a" if file_exists else "w"
    t0 = time.perf_counter()

    with open(csv_path, mode, newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Query", "Target", "RMSD", "TM_score", "Alignment_length"])
            f.flush()

        with Pool(processes=num_workers) as pool:
            with tqdm(
                total=n_tasks,
                desc="比对进度",
                unit="对",
                unit_scale=False,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            ) as pbar:
                for result in pool.imap_unordered(_worker_compare_tm_align, tasks, chunksize=chunk_size):
                    if result:
                        if collect_results:
                            results.append(result)
                        batch.append(result)
                        if write_batch_size > 0 and len(batch) >= write_batch_size:
                            for r in batch:
                                writer.writerow([
                                    r.query_name,
                                    r.target_name,
                                    f"{r.rmsd:.4f}",
                                    f"{r.tm_score:.4f}",
                                    r.alignment_length or "",
                                ])
                            f.flush()
                            total_written += len(batch)
                            batch = []
                    pbar.update()

        # 剩余批次
        if batch:
            for r in batch:
                writer.writerow([
                    r.query_name,
                    r.target_name,
                    f"{r.rmsd:.4f}",
                    f"{r.tm_score:.4f}",
                    r.alignment_length or "",
                ])
            total_written += len(batch)

    elapsed = time.perf_counter() - t0
    total_saved = len(results) if collect_results else total_written
    rate = n_tasks / elapsed if elapsed > 0 else 0
    logger.info(f"Saved {total_saved} comparison results to {csv_path}")
    logger.info(f"耗时 {elapsed:.1f}s，速度 {rate:.1f} 对/s")
    return results


def compare_structures_pairwise(
    structures: List[Path],
    output_dir: Path,
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    structure_names: Optional[List[str]] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
    resume: bool = False,
) -> List[ComparisonResult]:
    """
    对所有结构进行两两比对（多进程并行）。

    Args:
        structures: 结构 PDB 文件列表
        output_dir: 输出目录
        num_workers: 并行进程数
        chunk_size: 任务块大小
        structure_names: 结构名称列表（可选）
        write_batch_size: 每批写入条数，大批量时建议 10000–50000
        collect_results: 是否在内存中收集全部结果，百万级建议 False
        resume: 若为 True，跳过已有 (Query,Target) 对并追加写入，用于断点续跑

    Returns:
        比对结果列表
    """
    return batch_compare_tm_align(
        query_structures=structures,
        target_structures=structures,
        output_dir=output_dir,
        num_workers=num_workers,
        chunk_size=chunk_size,
        query_names=structure_names,
        target_names=structure_names,
        write_batch_size=write_batch_size,
        collect_results=collect_results,
        resume=resume,
    )


def plot_comparison_results(
    results: List[ComparisonResult],
    output_path: Path,
    title: str = "Structure Comparison Results"
):
    """
    绘制比对结果分布图
    
    Args:
        results: 比对结果列表
        output_path: 输出图片路径
        title: 图表标题
    """
    if not results:
        logger.warning("No results to plot")
        return
    
    rmsd_values = [r.rmsd for r in results]
    tm_values = [r.tm_score for r in results]
    
    plt.figure(figsize=(12, 5))
    
    # RMSD分布
    plt.subplot(1, 2, 1)
    plt.hist(rmsd_values, bins=20, edgecolor="black", color="skyblue")
    plt.xlabel("RMSD (Å)")
    plt.ylabel("Count")
    plt.title(f"RMSD Distribution ({title})")
    plt.axvline(np.mean(rmsd_values), color='red', linestyle='--', 
                label=f'Mean: {np.mean(rmsd_values):.2f} Å')
    plt.legend()
    
    # TM-score分布
    plt.subplot(1, 2, 2)
    plt.hist(tm_values, bins=20, edgecolor="black", color="orange")
    plt.xlabel("TM-score")
    plt.ylabel("Count")
    plt.title(f"TM-score Distribution ({title})")
    plt.axvline(np.mean(tm_values), color='red', linestyle='--',
                label=f'Mean: {np.mean(tm_values):.3f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    logger.info(f"Saved comparison plot to {output_path}")


def compare_against_reference(
    reference_pdb: Path,
    query_structures: List[Path],
    output_dir: Path,
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    reference_name: Optional[str] = None,
    query_names: Optional[List[str]] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
    resume: bool = False,
) -> List[ComparisonResult]:
    """
    将多个查询结构与一个参考结构进行比较（多进程并行）。

    Args:
        reference_pdb: 参考结构 PDB 文件
        query_structures: 查询结构 PDB 文件列表
        output_dir: 输出目录
        num_workers: 并行进程数
        chunk_size: 任务块大小
        reference_name: 参考结构名称（可选）
        query_names: 查询结构名称列表（可选）
        write_batch_size: 每批写入条数
        collect_results: 是否在内存中收集全部结果
        resume: 若为 True，跳过已有 (Query,Target) 对并追加写入，用于断点续跑

    Returns:
        比对结果列表
    """
    return batch_compare_tm_align(
        query_structures=[reference_pdb] * len(query_structures),
        target_structures=query_structures,
        output_dir=output_dir,
        num_workers=num_workers,
        chunk_size=chunk_size,
        query_names=[reference_name or reference_pdb.stem] * len(query_structures),
        target_names=query_names,
        write_batch_size=write_batch_size,
        collect_results=collect_results,
        resume=resume,
    )


def batch_compare_tm_align_from_dir(
    structures_dir: Path,
    output_dir: Path,
    pattern: str = "*.pdb",
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
    resume: bool = False,
) -> List[ComparisonResult]:
    """
    从目录中扫描 PDB 文件并进行两两 TM-align 比对（供 notebook 等调用）。

    高通量（如百万级）时建议：collect_results=False，write_batch_size=50000，
    num_workers 按机器核心数设置。

    Args:
        structures_dir: 存放 PDB 的目录
        output_dir: 输出目录
        pattern: 文件名通配符，默认 "*.pdb"
        num_workers: 并行进程数
        chunk_size: 任务块大小
        write_batch_size: 每批写入条数
        collect_results: 是否在内存中收集全部结果
        resume: 若为 True，跳过已有 (Query,Target) 对并追加写入，用于断点续跑

    Returns:
        比对结果列表（collect_results=False 时为空）
    """
    structures_dir = Path(structures_dir)
    if not structures_dir.exists():
        logger.error(f"structures_dir not found: {structures_dir}")
        return []
    structures = sorted(structures_dir.glob(pattern))
    if not structures:
        logger.warning(f"No files matching {pattern} in {structures_dir}")
        return []
    return compare_structures_pairwise(
        structures=structures,
        output_dir=output_dir,
        num_workers=num_workers,
        chunk_size=chunk_size,
        write_batch_size=write_batch_size,
        collect_results=collect_results,
        resume=resume,
    )


def batch_compare_tm_align_from_sample_dirs(
    parent_dir: Path,
    output_base: Path,
    pattern: str = "*.pdb",
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
    sample_dirs: Optional[List[str]] = None,
    min_pdbs: int = 1,
    resume: bool = False,
) -> Dict[str, List[ComparisonResult]]:
    """
    以「按样本分子」的目录为输入，对每个样本子目录内的 PDB 做两两 TM-align 比对。

    目录结构预期：
        parent_dir/
            sample_id_1/   (如 1001240_GCF_014200405.1)
                *.pdb
            sample_id_2/
                *.pdb
            ...

    每个样本的结果写入 output_base / sample_id / comparison_results.csv。

    Args:
        parent_dir: 顶层目录（如 esm3_structures_by_sample 的路径）
        output_base: 所有样本结果的根输出目录
        pattern: PDB 文件名通配符，默认 "*.pdb"
        num_workers: 并行进程数
        chunk_size: 任务块大小
        write_batch_size: 每批写入条数
        collect_results: 是否在内存中收集每个样本的结果
        sample_dirs: 若指定，仅处理这些子目录名；否则处理 parent_dir 下所有子目录
        min_pdbs: 至少需要多少个 PDB 才进行比对（默认 1，即至少有 1 个文件才参与）
        resume: 若为 True，每个样本跳过已有 (Query,Target) 对并追加写入，用于断点续跑

    Returns:
        样本 ID -> 该样本比对结果列表 的字典（collect_results=False 时值为空列表）
    """
    parent_dir = Path(parent_dir)
    output_base = Path(output_base)
    if not parent_dir.exists():
        logger.error(f"parent_dir not found: {parent_dir}")
        return {}

    if sample_dirs is not None:
        subdirs = [parent_dir / d for d in sample_dirs if (parent_dir / d).is_dir()]
    else:
        subdirs = [d for d in parent_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    all_results: Dict[str, List[ComparisonResult]] = {}
    subdirs_sorted = sorted(subdirs)
    n_samples = len(subdirs_sorted)
    t0 = time.perf_counter()
    with tqdm(
        subdirs_sorted,
        desc="样本进度",
        unit="样本",
        unit_scale=False,
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
    ) as pbar:
        for sample_path in pbar:
            sample_id = sample_path.name
            structures = sorted(sample_path.glob(pattern))
            if len(structures) < min_pdbs:
                logger.debug(f"Skip {sample_id}: only {len(structures)} PDB(s), need >= {min_pdbs}")
                pbar.set_postfix_str(sample_id[:20], refresh=False)
                continue
            pbar.set_postfix_str(sample_id[:20], refresh=False)
            sample_output = output_base / sample_id
            sample_output.mkdir(parents=True, exist_ok=True)
            results = compare_structures_pairwise(
                structures=structures,
                output_dir=sample_output,
                num_workers=num_workers,
                chunk_size=chunk_size,
                write_batch_size=write_batch_size,
                collect_results=collect_results,
                resume=resume,
            )
            all_results[sample_id] = results
            logger.info(f"Sample {sample_id}: {len(results)} comparisons -> {sample_output}")
    elapsed = time.perf_counter() - t0
    total_pairs = sum(len(r) for r in all_results.values())
    if elapsed > 0 and total_pairs > 0:
        logger.info(f"总耗时 {elapsed:.1f}s，共 {total_pairs} 对，平均 {total_pairs / elapsed:.1f} 对/s")
    return all_results


def run_tm_align_esm3_samples(
    parent_dir: Union[Path, str],
    output_base: Union[Path, str],
    resume: bool = False,
    plot: bool = False,
    pattern: str = "*.pdb",
    num_workers: Optional[int] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
    sample_dirs: Optional[List[str]] = None,
    min_pdbs: int = 1,
) -> Dict[str, List[ComparisonResult]]:
    """
    按样本目录运行 TM-align 比对（供 notebook / 脚本统一调用）。

    对 parent_dir 下每个样本子目录内的 PDB 做两两 TM-align，结果写入
    output_base/<sample_id>/comparison_results.csv。可选为每个样本生成 comparison_plot.png。

    Args:
        parent_dir: esm3_structures_by_sample 顶层目录
        output_base: 结果输出根目录
        resume: 是否断点续跑，跳过已有 (Query,Target) 对
        plot: 是否为每个样本生成 comparison_plot.png
        pattern: PDB 通配符
        num_workers: 并行进程数
        write_batch_size: 每批写入条数
        collect_results: 是否在内存中收集每个样本结果（plot=True 时需 True）
        sample_dirs: 仅处理这些样本子目录名；None 表示全部
        min_pdbs: 样本内至少多少个 PDB 才参与比对

    Returns:
        样本 ID -> 该样本比对结果列表
    """
    parent_dir = Path(parent_dir)
    output_base = Path(output_base)
    if plot and not collect_results:
        collect_results = True
        logger.info("plot=True 需要 collect_results，已自动开启")
    results_by_sample = batch_compare_tm_align_from_sample_dirs(
        parent_dir=parent_dir,
        output_base=output_base,
        pattern=pattern,
        num_workers=num_workers,
        write_batch_size=write_batch_size,
        collect_results=collect_results,
        sample_dirs=sample_dirs,
        min_pdbs=min_pdbs,
        resume=resume,
    )
    if plot:
        for sample_id, results in results_by_sample.items():
            if not results:
                continue
            plot_path = output_base / sample_id / "comparison_plot.png"
            try:
                plot_comparison_results(
                    results=results,
                    output_path=plot_path,
                    title=sample_id,
                )
            except Exception as e:
                logger.warning("绘制 %s 失败: %s", sample_id, e)
    return results_by_sample
