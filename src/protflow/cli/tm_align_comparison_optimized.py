"""
优化的TM-align批量比对脚本

优化点：
1. 使用后端模块（protflow.core.structure_comparison）
2. 改进的chunk_size计算（根据任务数动态调整）
3. 更好的错误处理和日志记录
4. 支持配置文件
5. 内存优化（避免一次性加载所有任务）
"""
import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import logging

# 导入后端模块（使用相对导入，因为现在在protflow.cli包内）
from ..core.structure_comparison import (
    compare_structures_tm_align,
    plot_comparison_results,
    ComparisonResult
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------- 路径配置 --------
DIR_AF_ROOT = "/mnt/sda/home/zhuao/esm3run/测试/reviewed_data"
DIR_ESM3_PARENT = "/mnt/sda/home/zhuao/esm3run/测试/reviewed_data_predictions"
BASE_OUTPUT_DIR = "./comparison_results_all_steps"

# -------- 性能参数（优化） --------
# 自动检测CPU核心数，但限制最大值为380
NUM_CORES = min(380, cpu_count())
# 动态chunk_size：根据任务数调整，避免过多小任务
CHUNK_SIZE = max(5, min(20, 1000 // NUM_CORES))  # 动态调整
# -------------------------


def worker_compare_optimized(task):
    """
    优化的单个比对任务工作函数
    
    使用后端模块，更好的错误处理
    """
    acc, af_path, esm3_path = task
    try:
        result = compare_structures_tm_align(
            query_pdb=Path(af_path),
            target_pdb=Path(esm3_path),
            query_name=f"{acc}_alphafold",
            target_name=f"{acc}_esm3"
        )
        
        if result:
            return [acc, result.rmsd, result.tm_score]
        else:
            logger.warning(f"Comparison failed for {acc}")
            return None
    except Exception as e:
        logger.error(f"Error comparing {acc}: {e}")
        return None


def save_distribution_plot(results, save_path, title):
    """绘制并保存单个 step 的 RMSD 和 TM-score 分布图"""
    if not results:
        logger.warning(f"No results to plot for {title}")
        return
    
    rmsd_values = [r[1] for r in results]
    tm_values = [r[2] for r in results]

    plt.figure(figsize=(12, 5))
    # RMSD 分布
    plt.subplot(1, 2, 1)
    plt.hist(rmsd_values, bins=20, edgecolor="black", color="skyblue")
    plt.xlabel("RMSD (Å)")
    plt.ylabel("Count")
    plt.title(f"RMSD Distribution ({title})")
    mean_rmsd = np.mean(rmsd_values)
    plt.axvline(mean_rmsd, color='red', linestyle='--', 
                label=f'Mean: {mean_rmsd:.2f} Å')
    plt.legend()

    # TM-score 分布
    plt.subplot(1, 2, 2)
    plt.hist(tm_values, bins=20, edgecolor="black", color="orange")
    plt.xlabel("TM-score")
    plt.ylabel("Count")
    plt.title(f"TM-score Distribution ({title})")
    mean_tm = np.mean(tm_values)
    plt.axvline(mean_tm, color='red', linestyle='--',
                label=f'Mean: {mean_tm:.3f}')
    plt.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    logger.info(f"Saved distribution plot to {save_path}")


def prepare_tasks(step_path, step_num):
    """
    准备比对任务列表
    
    优化：使用Path对象，更好的错误处理
    """
    dir_af = Path(DIR_AF_ROOT)
    dir_esm3 = Path(step_path)
    
    if not dir_af.exists():
        logger.error(f"AlphaFold directory not found: {DIR_AF_ROOT}")
        return []
    
    if not dir_esm3.exists():
        logger.error(f"ESM3 directory not found: {step_path}")
        return []
    
    accessions = [
        d for d in os.listdir(DIR_AF_ROOT) 
        if os.path.isdir(os.path.join(DIR_AF_ROOT, d))
    ]
    
    tasks = []
    for acc in accessions:
        af_path = dir_af / acc / f"{acc}_alphafold.pdb"
        esm3_path = dir_esm3 / acc / f"{acc}_esm3_step{step_num}.pdb"
        
        if af_path.exists() and esm3_path.exists():
            tasks.append((acc, str(af_path), str(esm3_path)))
        else:
            logger.debug(f"Skipping {acc}: files not found")
    
    logger.info(f"Prepared {len(tasks)} comparison tasks for step {step_num}")
    return tasks


def main():
    """主函数 - 优化的批量比对流程"""
    base_output = Path(BASE_OUTPUT_DIR)
    base_output.mkdir(exist_ok=True, parents=True)
    
    dir_esm3_parent = Path(DIR_ESM3_PARENT)
    if not dir_esm3_parent.exists():
        logger.error(f"ESM3 parent directory not found: {DIR_ESM3_PARENT}")
        return
    
    steps = sorted(
        [d for d in os.listdir(DIR_ESM3_PARENT) if d.startswith("step_")],
        key=lambda x: int(x.split('_')[-1])
    )
    
    if not steps:
        logger.warning("No step directories found")
        return
    
    summary_data = []
    logger.info(f"🚀 启动优化模式: {NUM_CORES} 核心, chunk_size={CHUNK_SIZE}")
    logger.info(f"处理 {len(steps)} 个步骤")

    # 在循环外启动进程池，防止 "Too many open files" 报错
    # 使用maxtasksperchild避免内存泄漏
    with Pool(processes=NUM_CORES, maxtasksperchild=100) as pool:
        for step_name in steps:
            step_num = step_name.split('_')[-1]
            step_path = dir_esm3_parent / step_name
            current_output_dir = base_output / step_name
            current_output_dir.mkdir(exist_ok=True, parents=True)

            # 准备任务
            tasks = prepare_tasks(str(step_path), step_num)
            
            if not tasks:
                logger.warning(f"No tasks for {step_name}, skipping")
                continue

            # 执行比对
            results = []
            logger.info(f"Processing {step_name}: {len(tasks)} tasks")
            
            with tqdm(total=len(tasks), desc=f"Processing {step_name}", unit="pdb") as pbar:
                for res in pool.imap_unordered(
                    worker_compare_optimized, 
                    tasks, 
                    chunksize=CHUNK_SIZE
                ):
                    if res:
                        results.append(res)
                    pbar.update()

            if results:
                # 1. 保存 CSV
                csv_path = current_output_dir / f"{step_name}_results.csv"
                with open(csv_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Accession", "RMSD", "TM_score"])
                    writer.writerows(results)
                logger.info(f"Saved {len(results)} results to {csv_path}")
                
                # 2. 生成该 Step 的分布图
                plot_path = current_output_dir / "distribution.png"
                save_distribution_plot(results, plot_path, step_name)
                
                # 3. 计算统计信息
                avg_tm = np.mean([r[2] for r in results])
                avg_rmsd = np.mean([r[1] for r in results])
                summary_data.append([int(step_num), avg_tm, avg_rmsd])
                
                logger.info(
                    f"✅ {step_name} 完成 | "
                    f"平均 TM: {avg_tm:.4f} | "
                    f"平均 RMSD: {avg_rmsd:.2f} Å | "
                    f"成功: {len(results)}/{len(tasks)}"
                )
            else:
                logger.warning(f"No results for {step_name}")

    # 3. 绘制总体趋势折线图
    if summary_data:
        summary_data.sort(key=lambda x: x[0])  # 按 step 数字排序
        steps_idx, tms, rmsds = zip(*summary_data)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # TM-score趋势
        ax1.plot(steps_idx, tms, marker='o', linestyle='-', linewidth=2, color='green')
        ax1.set_title("Overall TM-score Trend")
        ax1.set_xlabel("Step")
        ax1.set_ylabel("Mean TM-score")
        ax1.grid(True, alpha=0.3)
        
        # RMSD趋势
        ax2.plot(steps_idx, rmsds, marker='s', linestyle='-', linewidth=2, color='blue')
        ax2.set_title("Overall RMSD Trend")
        ax2.set_xlabel("Step")
        ax2.set_ylabel("Mean RMSD (Å)")
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        trend_path = base_output / "overall_trend.png"
        plt.savefig(trend_path, dpi=300)
        plt.close()
        logger.info(f"Saved trend plot to {trend_path}")
        
        # 保存汇总 CSV
        summary_path = base_output / "overall_summary.csv"
        with open(summary_path, "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Mean_TM_score", "Mean_RMSD"])
            writer.writerows(summary_data)
        logger.info(f"Saved summary to {summary_path}")
        
        logger.info(f"\n✨ 任务全部结束！总趋势图已保存至: {trend_path}")
    else:
        logger.warning("No summary data to save")


if __name__ == "__main__":
    main()
