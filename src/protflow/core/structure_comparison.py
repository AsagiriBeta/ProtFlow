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

    Returns:
        比对结果列表（当 collect_results=False 时为空列表）
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

    n_tasks = len(tasks)
    if n_tasks == 0:
        logger.warning("No tasks to run")
        return []

    if chunk_size is None:
        chunk_size = max(1, min(50, n_tasks // (num_workers * 4)))

    def worker_compare(task):
        query_pdb, target_pdb, query_name, target_name = task
        return compare_structures_tm_align(query_pdb, target_pdb, query_name, target_name)

    csv_path = output_dir / "comparison_results.csv"
    results: List[ComparisonResult] = []
    batch: List[ComparisonResult] = []
    total_written = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query", "Target", "RMSD", "TM_score", "Alignment_length"])
        f.flush()

        with Pool(processes=num_workers) as pool:
            with tqdm(total=n_tasks, desc="Comparing structures") as pbar:
                for result in pool.imap_unordered(worker_compare, tasks, chunksize=chunk_size):
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

    total_saved = len(results) if collect_results else total_written
    logger.info(f"Saved {total_saved} comparison results to {csv_path}")
    return results


def compare_structures_pairwise(
    structures: List[Path],
    output_dir: Path,
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    structure_names: Optional[List[str]] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
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
    )


def batch_compare_tm_align_from_dir(
    structures_dir: Path,
    output_dir: Path,
    pattern: str = "*.pdb",
    num_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
    write_batch_size: int = 10000,
    collect_results: bool = True,
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
    )
