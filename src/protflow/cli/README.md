# ProtFlow CLI 模块

此模块包含 ProtFlow 项目的命令行工具和实用脚本。

## 模块结构

所有命令行工具现在统一在 `protflow.cli` 包内，结构更清晰，导入更方便。

## 结构比对脚本

### tm_align_comparison.py
基础的 TM-align 批量比对脚本，用于比较 AlphaFold 和 ESM3 预测的蛋白质结构。

**使用方法：**
```bash
# 方法1: 作为模块运行（推荐）
python -m protflow.cli.tm_align_comparison

# 方法2: 直接运行脚本
python src/protflow/cli/tm_align_comparison.py
```

**配置参数：**
- `DIR_AF_ROOT`: AlphaFold 结构目录
- `DIR_ESM3_PARENT`: ESM3 预测结构目录
- `BASE_OUTPUT_DIR`: 输出目录
- `NUM_CORES`: 并行处理核心数
- `CHUNK_SIZE`: 任务分块大小

### tm_align_comparison_optimized.py
优化的 TM-align 比对脚本，包含以下改进：

1. **使用后端模块** - 调用 `protflow.core.structure_comparison`
2. **动态参数调整** - 根据任务数和CPU核心数自动调整chunk_size
3. **改进的错误处理** - 更详细的日志记录和错误恢复
4. **内存优化** - 使用 `maxtasksperchild` 避免内存泄漏
5. **更好的统计信息** - 包括 RMSD 趋势分析

**使用方法：**
```bash
# 方法1: 作为模块运行（推荐）
python -m protflow.cli.tm_align_comparison_optimized

# 方法2: 直接运行脚本
python src/protflow/cli/tm_align_comparison_optimized.py
```

**推荐使用优化版本**，它提供了更好的性能和错误处理。

### tm_align_esm3_samples.py（esm3_structures_by_sample 输入）

以 **按样本分子** 的目录（如 ESM3 预测输出的 `esm3_structures_by_sample`）为输入，对每个样本子目录内的 PDB 做两两 TM-align 比对。该目录通常由外部 ESM3 预测脚本生成（例如从 prokka 的 .faa 预测结构并保存为 `esm3_structures_by_sample/<sample_id>/*.pdb`）；本脚本仅负责**比对**步骤，不依赖具体预测脚本。

**目录结构预期：**
```
esm3_structures_by_sample/
    1001240_GCF_014200405.1/
        CHDELLME_00003.pdb
        CHDELLME_01426.pdb
        ...
    2582905_GCF_005954645.2/
        *.pdb
    ...
```

每个样本的结果写入 `output_base/<sample_id>/comparison_results.csv`。

**使用方法：**
```bash
# 指定输入/输出（推荐）
python -m protflow.cli.tm_align_esm3_samples --input /path/to/esm3_structures_by_sample --output ./outputs/tm_align_by_sample

# 使用环境变量
export ESM3_STRUCTURES_BY_SAMPLE=/path/to/esm3_structures_by_sample
python -m protflow.cli.tm_align_esm3_samples

# 仅处理部分样本、生成分布图
python -m protflow.cli.tm_align_esm3_samples -i /path/to/esm3_structures_by_sample -o ./out --sample 1001240_GCF_014200405.1 --plot
```

**参数说明：**
- `--input` / `-i`: esm3_structures_by_sample 顶层目录（默认：`~/esm3run/predicted/esm3_structures_by_sample` 或环境变量 `ESM3_STRUCTURES_BY_SAMPLE`）
- `--output` / `-o`: 结果输出根目录（默认：`outputs/tm_align_by_sample` 或环境变量 `TM_ALIGN_OUTPUT`）
- `--pattern`: PDB 通配符（默认 `*.pdb`）
- `--num-workers`: 并行进程数
- `--no-collect-results`: 大批量时仅写 CSV、不收集到内存
- `--min-pdbs`: 样本内至少多少个 PDB 才参与比对
- `--sample`: 仅处理指定样本（可多次）
- `--plot`: 为每个样本生成 comparison_plot.png
- `--resume`: 断点续跑，跳过已有 (Query,Target) 对，只跑未完成任务并追加写入；中断后再次运行加此参数即可从中断处继续

## 其他脚本

- `runner.py` - 主运行脚本
- `check_deps.py` - 依赖检查脚本
- `validate_notebook.py` - Notebook 验证脚本
- `setup_*.sh` - 环境设置脚本

## 注意事项

1. 运行脚本前，请确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   pip install tmtools  # 用于TM-align比对
   ```

2. 脚本中的路径配置需要根据实际环境修改

3. 对于大规模比对任务，建议使用优化版本脚本

4. 结果文件默认保存在当前目录，建议指定输出目录到 `outputs/`
