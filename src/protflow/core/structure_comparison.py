"""
结构比对工具模块 - 支持TM-align和DALI比对

提供批量结构比对功能，支持：
- TM-align比对（使用tmtools）
- DALI比对（使用protflow.prediction.dali）
- 批量处理和结果汇总
"""
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
import csv
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool
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
    num_workers: int = 4,
    chunk_size: int = 5,
    query_names: Optional[List[str]] = None,
    target_names: Optional[List[str]] = None
) -> List[ComparisonResult]:
    """
    批量使用TM-align比较结构
    
    Args:
        query_structures: 查询结构PDB文件列表
        target_structures: 目标结构PDB文件列表
        output_dir: 输出目录
        num_workers: 并行工作进程数
        chunk_size: 每个工作进程的chunk大小
        query_names: 查询结构名称列表（可选）
        target_names: 目标结构名称列表（可选）
    
    Returns:
        比对结果列表
    """
    if not TMTools_AVAILABLE:
        logger.error("tmtools not available. Install with: pip install tmtools")
        return []
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 准备任务
    tasks = []
    for i, query_pdb in enumerate(query_structures):
        for j, target_pdb in enumerate(target_structures):
            query_name = query_names[i] if query_names and i < len(query_names) else query_pdb.stem
            target_name = target_names[j] if target_names and j < len(target_names) else target_pdb.stem
            tasks.append((query_pdb, target_pdb, query_name, target_name))
    
    def worker_compare(task):
        """单个比对任务的工作函数"""
        query_pdb, target_pdb, query_name, target_name = task
        return compare_structures_tm_align(query_pdb, target_pdb, query_name, target_name)
    
    # 执行批量比对
    results = []
    with Pool(processes=num_workers) as pool:
        with tqdm(total=len(tasks), desc="Comparing structures") as pbar:
            for result in pool.imap_unordered(worker_compare, tasks, chunksize=chunk_size):
                if result:
                    results.append(result)
                pbar.update()
    
    # 保存结果
    csv_path = output_dir / "comparison_results.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Query", "Target", "RMSD", "TM_score", "Alignment_length"])
        for r in results:
            writer.writerow([
                r.query_name,
                r.target_name,
                f"{r.rmsd:.4f}",
                f"{r.tm_score:.4f}",
                r.alignment_length or ""
            ])
    
    logger.info(f"Saved {len(results)} comparison results to {csv_path}")
    
    return results


def compare_structures_pairwise(
    structures: List[Path],
    output_dir: Path,
    num_workers: int = 4,
    chunk_size: int = 5,
    structure_names: Optional[List[str]] = None
) -> List[ComparisonResult]:
    """
    对所有结构进行两两比对
    
    Args:
        structures: 结构PDB文件列表
        output_dir: 输出目录
        num_workers: 并行工作进程数
        chunk_size: 每个工作进程的chunk大小
        structure_names: 结构名称列表（可选）
    
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
        target_names=structure_names
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
    num_workers: int = 4,
    chunk_size: int = 5,
    reference_name: Optional[str] = None,
    query_names: Optional[List[str]] = None
) -> List[ComparisonResult]:
    """
    将多个查询结构与一个参考结构进行比较
    
    Args:
        reference_pdb: 参考结构PDB文件
        query_structures: 查询结构PDB文件列表
        output_dir: 输出目录
        num_workers: 并行工作进程数
        chunk_size: 每个工作进程的chunk大小
        reference_name: 参考结构名称（可选）
        query_names: 查询结构名称列表（可选）
    
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
        target_names=query_names
    )
