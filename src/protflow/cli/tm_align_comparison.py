"""
TM-align批量比对脚本

用于批量比较AlphaFold和ESM3预测的蛋白质结构。

使用方法：
    python -m protflow.cli.tm_align_comparison
    或
    python src/protflow/cli/tm_align_comparison.py
"""
import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from tmtools import tm_align
from tmtools.io import get_structure, get_residue_data

# -------- 路径配置 --------
# 请根据实际情况修改以下路径
DIR_AF_ROOT = "/mnt/sda/home/zhuao/esm3run/测试/reviewed_data"
DIR_ESM3_PARENT = "/mnt/sda/home/zhuao/esm3run/测试/reviewed_data_predictions"
BASE_OUTPUT_DIR = "./comparison_results_all_steps"

# -------- 性能参数 --------
NUM_CORES = 380 
CHUNK_SIZE = 5   
# -------------------------

def worker_compare(task):
    """单个比对任务的工作函数"""
    acc, af_path, esm3_path = task
    try:
        s1 = get_structure(af_path)
        s2 = get_structure(esm3_path)
        chain1 = next(s1.get_chains())
        chain2 = next(s2.get_chains())
        coords1, seq1 = get_residue_data(chain1)
        coords2, seq2 = get_residue_data(chain2)
        result = tm_align(coords1, coords2, seq1, seq2)
        mean_tm = (result.tm_norm_chain1 + result.tm_norm_chain2) / 2
        return [acc, result.rmsd, mean_tm]
    except Exception:
        return None

def save_distribution_plot(results, save_path, title):
    """绘制并保存单个 step 的 RMSD 和 TM-score 分布图"""
    rmsd_values = [r[1] for r in results]
    tm_values = [r[2] for r in results]

    plt.figure(figsize=(12, 5))
    # RMSD 分布
    plt.subplot(1, 2, 1)
    plt.hist(rmsd_values, bins=20, edgecolor="black", color="skyblue")
    plt.xlabel("RMSD (Å)")
    plt.ylabel("Count")
    plt.title(f"RMSD Distribution ({title})")

    # TM-score 分布
    plt.subplot(1, 2, 2)
    plt.hist(tm_values, bins=20, edgecolor="black", color="orange")
    plt.xlabel("TM-score")
    plt.ylabel("Count")
    plt.title(f"TM-score Distribution ({title})")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def main():
    if not os.path.exists(BASE_OUTPUT_DIR):
        os.makedirs(BASE_OUTPUT_DIR)

    steps = sorted(
        [d for d in os.listdir(DIR_ESM3_PARENT) if d.startswith("step_")],
        key=lambda x: int(x.split('_')[-1])
    )

    summary_data = []
    print(f"🚀 启动 380 核强力模式...")

    # 在循环外启动进程池，防止 "Too many open files" 报错
    with Pool(processes=NUM_CORES) as pool:
        for step_name in steps:
            step_num = step_name.split('_')[-1]
            step_path = os.path.join(DIR_ESM3_PARENT, step_name)
            current_output_dir = os.path.join(BASE_OUTPUT_DIR, step_name)
            os.makedirs(current_output_dir, exist_ok=True)

            # 准备任务
            accessions = [d for d in os.listdir(DIR_AF_ROOT) if os.path.isdir(os.path.join(DIR_AF_ROOT, d))]
            tasks = []
            for acc in accessions:
                af_path = os.path.join(DIR_AF_ROOT, acc, f"{acc}_alphafold.pdb")
                esm3_path = os.path.join(step_path, acc, f"{acc}_esm3_step{step_num}.pdb")
                if os.path.exists(af_path) and os.path.exists(esm3_path):
                    tasks.append((acc, af_path, esm3_path))

            if not tasks: continue

            # 执行比对
            results = []
            with tqdm(total=len(tasks), desc=f"Processing {step_name}", unit="pdb") as pbar:
                for res in pool.imap_unordered(worker_compare, tasks, chunksize=CHUNK_SIZE):
                    if res: results.append(res)
                    pbar.update()

            if results:
                # 1. 保存 CSV
                csv_path = os.path.join(current_output_dir, f"{step_name}_results.csv")
                with open(csv_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Accession", "RMSD", "TM_score"])
                    writer.writerows(results)
                
                # 2. 生成该 Step 的分布图 (对应你原脚本的图片)
                plot_path = os.path.join(current_output_dir, "distribution.png")
                save_distribution_plot(results, plot_path, step_name)
                
                avg_tm = np.mean([r[2] for r in results])
                summary_data.append([int(step_num), avg_tm])
                print(f"✅ {step_name} 完成 | 平均 TM: {avg_tm:.4f} | 图片已保存")

    # 3. 绘制总体趋势折线图
    if summary_data:
        summary_data.sort() # 按 step 数字排序
        steps_idx, tms = zip(*summary_data)
        
        plt.figure(figsize=(10, 6))
        plt.plot(steps_idx, tms, marker='o', linestyle='-', linewidth=2, color='green')
        plt.title("Overall TM-score Trend")
        plt.xlabel("Step")
        plt.ylabel("Mean TM-score")
        plt.grid(True, alpha=0.3)
        trend_path = os.path.join(BASE_OUTPUT_DIR, "overall_trend.png")
        plt.savefig(trend_path, dpi=300)
        plt.close()
        
        # 保存汇总 CSV
        with open(os.path.join(BASE_OUTPUT_DIR, "overall_summary.csv"), "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Step", "Mean_TM_score"])
            writer.writerows(summary_data)
        
        print(f"\n✨ 任务全部结束！总趋势图已保存至: {trend_path}")

if __name__ == "__main__":
    main()