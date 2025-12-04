# ProtFlow Notebooks

本目录包含 ProtFlow 项目的 Jupyter Notebook 工作流。所有 notebooks 现在使用共享的工具和标准化的初始化流程。

## 📁 目录结构

```
notebooks/
├── core/           # 核心工作流 (00-09)
├── tools/          # 单独工具 (10-19)
├── analysis/       # 分析工具 (20-29)
└── templates/      # 初始化模板
```

## 🚀 快速开始

### 1. 使用已有的 Notebook

所有 notebooks 现在都使用标准化的初始化单元格，会自动：
- ✅ 检查并安装所需依赖
- ✅ 设置项目路径和工作目录
- ✅ 导入常用模块
- ✅ 从 `src/protflow` 导入功能

只需打开 notebook 并运行所有单元格即可。

### 2. 创建新的 Notebook

从 `templates/` 目录复制适当的初始化模板：

**对于 ESM3 结构预测 notebook：**
```python
# 复制 templates/esm3_notebook_init.py 的内容到第一个代码单元格
```

**对于分析 notebook：**
```python
# 复制 templates/analysis_notebook_init.py 的内容到第一个代码单元格
```

**对于使用 Conda 工具的 notebook：**
```python
# 复制 templates/conda_tool_notebook_init.py 的内容到第一个代码单元格
```

## 📚 可用的 Notebooks

### 核心工作流 (Core Workflows)

| Notebook | 描述 | Colab |
|----------|------|-------|
| `00_genome_annotation_to_structure.ipynb` | 完整流程：Prokka → ESM3 → DALI | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/00_genome_annotation_to_structure.ipynb) |
| `01_protein_structure_prediction.ipynb` | ESM3 蛋白质结构预测 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/01_protein_structure_prediction.ipynb) |
| `02_pocket_detection_p2rank.ipynb` | P2Rank 口袋检测 | - |
| `03_ligand_docking_vina.ipynb` | AutoDock Vina 配体对接 | - |

### 工具 (Tools)

| Notebook | 描述 |
|----------|------|
| `10_genome_annotation_prokka.ipynb` | Prokka 基因组注释 |
| `11_protein_structure_esm3.ipynb` | ESM3 结构预测工具 |
| `12_structure_alignment_dali.ipynb` | DALI 结构比对 |
| `13_biosynthetic_cluster_antismash.ipynb` | antiSMASH 生物合成簇分析 |

### 分析 (Analysis)

| Notebook | 描述 | 状态 |
|----------|------|------|
| `20_cds_annotation_comparison.ipynb` | CDS 注释比较 | ✅ 已更新 |
| `21_batch_structure_analysis.ipynb` | 批量结构分析 | ✅ 已更新 |

## 🛠️ 使用共享工具

所有 notebooks 现在可以直接从 `protflow` 模块导入功能：

```python
# 结构预测
from protflow.prediction.esm3_predict import predict_structure

# 口袋检测
from protflow.docking.p2rank import detect_pockets

# 序列解析
from protflow.utils.seq_parser import parse_genbank, extract_sequences

# CDS 比较
from protflow.core.cds_comparison import compare_annotations

# Notebook 工具
from protflow.utils.notebook_utils import (
    check_and_install_packages,
    setup_notebook_environment,
    ensure_conda_env
)
```

## 📋 依赖管理

### 自动安装

所有 notebooks 使用 `notebook_utils` 中的函数自动检查和安装依赖：

```python
from protflow.utils.notebook_utils import check_and_install_packages

# 自动检查并安装缺失的包
check_and_install_packages(['numpy', 'pandas', 'biopython'])
```

### 预定义包组

- `CORE_PACKAGES`: 核心依赖 (biopython, pandas, numpy, tqdm)
- `ESM3_PACKAGES`: ESM3 相关包
- `VISUALIZATION_PACKAGES`: 可视化包
- `NOTEBOOK_PACKAGES`: Notebook 相关包

## 🔄 迁移现有 Notebook

如果你有旧的 notebook 需要更新：

1. 查看 `docs/notebook-migration-guide.md` 获取详细指南
2. 参考 `templates/` 中的模板
3. 查看已更新的 notebooks 作为示例（如 `analysis/20_*.ipynb`）

### 简要步骤：

1. **删除旧的初始化代码**
   - 手动包安装代码
   - 手动环境设置
   - 重复的导入语句

2. **添加新的初始化单元格**
   - 从 `templates/` 复制适当的模板
   - 根据需要自定义 `work_dir_name`

3. **使用 src 中的代码**
   - 将自定义函数移到 `src/protflow/` 适当的模块
   - 在 notebook 中导入使用

## 💡 最佳实践

1. **始终使用模板**：从 `templates/` 开始新的 notebook
2. **重用代码**：将通用函数放在 `src/protflow/` 中
3. **保持简洁**：notebook 应关注工作流程，不是实现细节
4. **文档化**：添加 markdown 单元格解释每个步骤
5. **测试**：在提交前运行整个 notebook

## 🔍 故障排除

### 导入错误

如果遇到 `ModuleNotFoundError: No module named 'protflow'`:

```python
# 确保初始化单元格包含这些行：
import sys
from pathlib import Path

project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:
    project_root = project_root.parent

if (project_root / 'src').exists():
    src_dir = str(project_root / 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
```

### 依赖安装失败

如果自动安装失败，手动安装：

```bash
pip install -r requirements.txt
```

或者安装特定包：

```bash
pip install biopython pandas numpy tqdm
```

## 📖 更多资源

- [完整文档](../docs/README.md)
- [迁移指南](../docs/notebook-migration-guide.md)
- [API 参考](../docs/developer-guide/api-reference.md)
- [故障排除](../docs/user-guide/tutorial/troubleshooting.md)

## 🤝 贡献

欢迎贡献新的 notebooks 或改进现有的！请：

1. 使用适当的模板开始
2. 遵循现有的命名约定
3. 添加清晰的文档
4. 在 PR 中包含示例输出

## 📝 更新日志

- **2024-12**: 添加共享工具和标准化初始化
- **2024-11**: 重构 notebook 组织结构
- **2024-10**: 初始 notebooks 创建
