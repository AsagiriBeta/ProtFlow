# ProtFlow Notebooks

本目录包含 ProtFlow 项目的 Jupyter Notebook 工作流。所有 notebooks 使用统一的初始化函数，仅包含前端调用代码，所有业务逻辑在 `src/protflow` 中。

## 📁 目录结构

```
notebooks/
├── core/           # 核心工作流 (00-09)
│   ├── 00_genome_annotation_to_structure.ipynb  # Prokka → ESM3 → DALI
│   ├── 01_protein_structure_prediction.ipynb    # ESM3 结构预测
│   ├── 02_pocket_detection_p2rank.ipynb         # P2Rank 口袋检测
│   └── 03_ligand_docking_vina.ipynb             # AutoDock Vina 对接
├── tools/          # 单独工具 (10-19)
│   ├── 10_genome_annotation_prokka.ipynb        # Prokka 注释
│   ├── 11_protein_structure_esm3.ipynb          # ESM3 预测工具
│   ├── 12_structure_alignment_dali.ipynb       # DALI 结构比对
│   └── 13_biosynthetic_cluster_antismash.ipynb  # antiSMASH 分析
└── analysis/       # 分析工具 (20-29)
    ├── 20_cds_annotation_comparison.ipynb       # CDS 注释比较
    ├── 21_batch_structure_analysis.ipynb         # 批量结构分析
    ├── 22_structure_comparison_tm_align.ipynb    # TM-align 结构比较（单目录）
    └── 23_structure_comparison_tm_align_by_sample.ipynb  # TM-align 按样本目录（esm3_structures_by_sample）
```

## 🚀 快速开始

### 统一初始化模板

所有 notebooks 使用 `init_notebook()` 函数进行初始化：

> 📖 **详细模板**：查看 [TEMPLATE.md](TEMPLATE.md) 了解完整的 notebook 模板和精简原则

```python
# 1. 基础初始化（自动检测环境、设置路径、安装依赖）
from protflow.utils.notebook_utils import init_notebook, ESM3_PACKAGES

paths = init_notebook('my_workflow', packages=ESM3_PACKAGES)
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

# 2. 导入后端模块（所有业务逻辑在后端）
from protflow.prediction.esm3_predict import predict_structures_from_fasta, ESM3GenerationConfig

# 3. 调用后端函数
results = predict_structures_from_fasta(...)
```

### 功能分类

#### 1. 核心工作流 (core/)
完整的端到端分析流程，包含多个步骤。

#### 2. 工具 (tools/)
单个功能的独立工具，可单独使用。

#### 3. 分析 (analysis/)
结果分析和比较工具。

## 📚 Notebook 列表

### 核心工作流

| Notebook | 功能 | 后端模块 |
|----------|------|----------|
| `00_genome_annotation_to_structure.ipynb` | Prokka → ESM3 → DALI 完整流程 | `protflow.core.pipeline` |
| `01_protein_structure_prediction.ipynb` | ESM3 蛋白质结构预测 | `protflow.prediction.esm3_predict` |
| `02_pocket_detection_p2rank.ipynb` | P2Rank 口袋检测 | `protflow.docking.p2rank` |
| `03_ligand_docking_vina.ipynb` | AutoDock Vina 配体对接 | `protflow.docking.vina_dock` |

### 工具

| Notebook | 功能 | 后端模块 |
|----------|------|----------|
| `10_genome_annotation_prokka.ipynb` | Prokka 基因组注释 | `protflow.utils.prokka_utils` |
| `11_protein_structure_esm3.ipynb` | ESM3 结构预测工具 | `protflow.prediction.esm3_predict` |
| `12_structure_alignment_dali.ipynb` | DALI 结构比对 | `protflow.prediction.dali` |
| `13_biosynthetic_cluster_antismash.ipynb` | antiSMASH 分析 | `protflow.core.antismash` |

### 分析

| Notebook | 功能 | 后端模块 |
|----------|------|----------|
| `20_cds_annotation_comparison.ipynb` | CDS 注释比较 | `protflow.core.cds_comparison` |
| `21_batch_structure_analysis.ipynb` | 批量结构分析 | `protflow.core.structure_analysis` |
| `22_structure_comparison_tm_align.ipynb` | TM-align 结构比较（单目录） | `protflow.core.structure_comparison` |
| `23_structure_comparison_tm_align_by_sample.ipynb` | TM-align 按样本目录（esm3_structures_by_sample） | `protflow.core.structure_comparison` |

## 🛠️ 使用后端模块

所有 notebooks 只包含前端调用代码，业务逻辑都在 `src/protflow` 中：

```python
# ✅ 正确：直接调用后端函数
from protflow.prediction.esm3_predict import predict_structures_from_fasta
results = predict_structures_from_fasta(fasta_file, out_dir, ...)

# ❌ 错误：在 notebook 中实现业务逻辑
def predict_structures(...):  # 不要这样做
    # 业务逻辑应该在后端
    pass
```

### 常用后端模块

```python
# 结构预测
from protflow.prediction.esm3_predict import (
    load_esm3_small,
    predict_structures_from_fasta,
    ESM3GenerationConfig
)

# 序列处理
from protflow.utils.seq_parser import (
    extract_proteins_from_gbk,
    filter_and_select
)

# 结构分析
from protflow.core.structure_analysis import collect_structure_files
from protflow.core.structure_comparison import compare_structures_tm_align

# 口袋检测
from protflow.docking.p2rank import run_p2rank_on_pdbs

# 配体对接
from protflow.docking.vina_dock import run_vina
```

## 📋 依赖管理

### 预定义包组

```python
from protflow.utils.notebook_utils import (
    CORE_PACKAGES,      # 基础包：biopython, pandas, numpy, tqdm
    ESM3_PACKAGES,      # ESM3 相关包
    VISUALIZATION_PACKAGES,  # 可视化包
)

# 使用
paths = init_notebook('workflow', packages=ESM3_PACKAGES)
```

### 自定义包

```python
paths = init_notebook('workflow', packages=[
    'numpy',
    'pandas',
    ('cv2', 'opencv-python'),  # 导入名和包名不同时使用元组
])
```

## 💡 最佳实践

1. **保持简洁**：notebook 只包含前端调用，不包含业务逻辑
2. **使用统一初始化**：所有 notebooks 使用 `init_notebook()` 函数
3. **调用后端模块**：所有功能都从 `protflow.*` 模块导入
4. **文档化**：添加清晰的 markdown 单元格说明每个步骤
5. **测试**：提交前运行整个 notebook 确保正常工作

### 精简现有 Notebooks

如果现有 notebook 包含重复代码或业务逻辑，请参考 [TEMPLATE.md](TEMPLATE.md) 进行精简：

1. **替换初始化代码**：使用 `init_notebook()` 替换手动路径设置和依赖安装
2. **移除业务逻辑**：将自定义函数移到 `src/protflow/` 相应模块
3. **简化导入**：只导入需要的函数，不要导入整个模块

## 🔍 故障排除

### 导入错误

如果遇到 `ModuleNotFoundError: No module named 'protflow'`：

```python
# 使用 init_notebook() 会自动处理路径
from protflow.utils.notebook_utils import init_notebook
paths = init_notebook('workflow')
```

### 依赖安装失败

```bash
# 手动安装
pip install -r requirements.txt

# 或安装特定包
pip install biopython pandas numpy tqdm
```

## 📖 更多资源

- [项目 README](../README.md)
- [API 文档](../src/protflow/README.md)
