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

**说明：** 本脚本做的是「样本内两两比对」。若要做 **ESM3 预测 vs 参考目录（如 bf_structure）**，即每个 ESM3 对参考目录内全部 PDB 做 TM-align，请用下面的 **tm_align_esm3_vs_reference.py**。

---

### tm_align_esm3_vs_reference.py（ESM3 vs 参考目录，如 bf_structure）

以 **esm3_structures_by_sample** 为查询、以 **参考目录（如 bf_structure）** 为目标：对每个样本内的每个 ESM3 结构与参考目录内**全部** PDB 做 TM-align。Query=ESM3 预测，Target=参考结构。

**目录结构预期：**
- 输入(ESM3)：`esm3_structures_by_sample/<sample_id>/*.pdb`
- 参考目录：如 `~/esm3run/TPS_database/reviewed_results/bf_structure/*.pdb`

**使用方法：**
```bash
cd /path/to/ProtFlow

# 推荐：ESM3 预测 vs bf_structure，降低内存
python -m protflow.cli.tm_align_esm3_vs_reference \
  --input ~/esm3run/predicted/esm3_structures_by_sample \
  --reference ~/esm3run/TPS_database/reviewed_results/bf_structure \
  --output ./tm_align_esm3_vs_bf_structure \
  --no-collect-results \
  --num-workers 4 \
  --write-batch-size 50000
```

**参数说明：**
- `--input` / `-i`: esm3_structures_by_sample 顶层目录（默认：`~/esm3run/predicted/esm3_structures_by_sample`）
- `--reference` / `-r`: 参考 PDB 目录，如 bf_structure（默认：`~/esm3run/TPS_database/reviewed_results/bf_structure`）
- `--output` / `-o`: 结果输出根目录（默认：`tm_align_esm3_vs_reference`）
- 其余与 tm_align_esm3_samples 类似：`--pattern`、`--num-workers`、`--no-collect-results`、`--min-pdbs`、`--sample`、`--plot`、`--resume`

**输出：** `<output>/<sample_id>/comparison_results.csv`，每行为 (Query=ESM3, Target=参考, RMSD, TM_score, Alignment_length)。

大批量时建议加 `--no-collect-results`、适当减小 `--num-workers`；断点续跑加 `--resume`。

---

### import_tm_align_csv_to_db.py（CSV 导入数据库）

将 **tm_align_by_sample**（或任意「样本子目录 + comparison_results.csv」）下的所有 CSV 导入 **SQLite**，便于按样本/query/target 查询、聚合和与其它表关联。

**目录结构预期：**
```
tm_align_by_sample/   # 或 outputs/tm_align_by_sample 等
    sample_id_1/
        comparison_results.csv   # 表头: Query, Target, RMSD, TM_score, Alignment_length
    sample_id_2/
        comparison_results.csv
    ...
```

**使用方法：**
```bash
# 项目根目录下的 tm_align_by_sample 导入到当前目录的 tm_align_results.db
python -m protflow.cli.import_tm_align_csv_to_db --input ./tm_align_by_sample --output ./tm_align_results.db

# 指定路径与数据库名
python -m protflow.cli.import_tm_align_csv_to_db -i /path/to/tm_align_by_sample -o ./results/tm_align.db

# 清空表后重新导入（--replace 会先 DROP 表再创建）
python -m protflow.cli.import_tm_align_csv_to_db -i ./tm_align_by_sample -o ./tm_align_results.db --replace

# 只导入指定样本
python -m protflow.cli.import_tm_align_csv_to_db -i ./tm_align_by_sample -o ./tm_align_results.db --sample-dirs 1001240_GCF_014200405.1 2582905_GCF_005954645.2
```

**参数说明：**
- `--input` / `-i`: tm_align_by_sample 根目录（必填）
- `--output` / `-o`: 输出的 SQLite 文件路径（默认：`tm_align_results.db`）
- `--replace`: 若表已存在则先删除再创建；默认仅追加，重复的 (sample_id, query, target) 会跳过
- `--csv-name`: 每个样本目录下的 CSV 文件名（默认：`comparison_results.csv`）
- `--sample-dirs`: 仅导入这些样本子目录名；不指定则导入所有子目录
- `--batch-size`: 每批写入行数（默认：5000）

**数据库表结构（`tm_align_results`）：**
- `id`：自增主键
- `sample_id`：样本目录名
- `query`, `target`：比对对名称
- `rmsd`, `tm_score`：数值
- `alignment_length`：可选
- `source_file`：来源 CSV 路径
- `created_at`：插入时间  
唯一约束：`(sample_id, query, target)`，重复行会自动跳过。

**在 Python / notebook 中查询示例：**
```python
import sqlite3
from pathlib import Path

conn = sqlite3.connect("tm_align_results.db")
# 按样本统计
for row in conn.execute(
    "SELECT sample_id, COUNT(*), AVG(tm_score) FROM tm_align_results GROUP BY sample_id"
):
    print(row)
# 某样本内 TM-score 最高的前 10 对
for row in conn.execute(
    "SELECT query, target, tm_score FROM tm_align_results WHERE sample_id = ? ORDER BY tm_score DESC LIMIT 10",
    ("1001240_GCF_014200405.1",),
):
    print(row)
conn.close()
```

---

### blastp_tm_filter.py（TM-align 筛选 + BLASTP）

从 **tm_align_results** 表中筛出 **TM-score > 阈值** 且 **RMSD < 阈值** 的 (query, target) 对，用 Prokka 的 query 序列与 bf_seq 的 target 序列做 **BLASTP**，结果写入同库的 **blast_results** 表。

**默认筛选条件：** TM-score > 0.75，RMSD < 3.5。

**用法：**
```bash
python -m protflow.cli.blastp_tm_filter \
  --db ./tm_align_results.db \
  --prokka /path/to/prokka_results \
  --bf-seq /path/to/bf_seq \
  --tm-cutoff 0.75 \
  --rmsd-cutoff 3.5 \
  -w 150
```

**参数说明：**
- `--db`: 含 tm_align_results 的 SQLite 库路径
- `--prokka`: Prokka 结果根目录（每样本一子目录，内含 .faa）
- `--bf-seq`: 参考序列目录（bf_seq，.fasta/.fa）
- `--tm-cutoff`: TM-score 下限（默认 0.75）
- `--rmsd-cutoff`: RMSD 上限（默认 3.5）
- `-w` / `--workers`: BLASTP 并发进程数（默认 150）

**依赖：** 需安装 BLAST+（`blastp` 在 PATH）、Biopython。结果表 `blast_results` 字段：sample_id, query, target, e_value, score, identity。

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
