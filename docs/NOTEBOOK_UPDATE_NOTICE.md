# Notebook 优化更新说明

## 🎉 新功能

ProtFlow notebooks 已经优化，现在更简洁、更易用！

### 主要改进

1. **自动依赖管理** ✨
   - 无需手动安装包
   - 自动检测并安装缺失的依赖
   - 智能包管理

2. **标准化初始化** 📝
   - 所有 notebooks 使用统一的设置方式
   - 一个单元格完成所有初始化
   - 清晰的代码结构

3. **代码重用** ♻️
   - 从 `src/protflow/` 导入共享功能
   - 无需在 notebooks 中重复定义函数
   - 更易于维护

## 快速开始

### 使用现有 Notebooks

打开任何 notebook 并运行所有单元格 - 就这么简单！依赖会自动安装。

### 创建新 Notebooks

从模板开始：

```python
# 对于 ESM3 notebooks - 复制这段代码
from protflow.utils.notebook_utils import setup_esm3_notebook
paths = setup_esm3_notebook(work_dir_name='my_analysis')
```

```python
# 对于分析 notebooks - 复制这段代码
from protflow.utils.notebook_utils import setup_analysis_notebook
paths = setup_analysis_notebook(work_dir_name='my_analysis')
```

完整模板在 `notebooks/templates/` 目录。

## 示例对比

### 之前 😓

```python
# Cell 1
import sys, os
from pathlib import Path
PROJECT_ROOT = Path(...)
...

# Cell 2
import subprocess
def install_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call(...)
for pkg in ["torch", "pandas", ...]:
    install_package(pkg)

# Cell 3
import torch
import pandas as pd
...
```

### 现在 😊

```python
# 一个单元格搞定！
from protflow.utils.notebook_utils import setup_esm3_notebook
paths = setup_esm3_notebook(work_dir_name='esm3_runs')

# 已自动处理：
# ✓ 路径设置
# ✓ 依赖安装
# ✓ 常用导入
```

## 已更新的 Notebooks

- ✅ `analysis/20_cds_annotation_comparison.ipynb`
- ✅ `analysis/21_batch_structure_analysis.ipynb`

其他 notebooks 将逐步更新。未更新的 notebooks 仍然可以正常工作。

## 可用工具

现在可以直接导入：

```python
# 结构预测
from protflow.prediction.esm3_predict import predict_structure

# CDS 比较
from protflow.core import cds_comparison

# 序列解析
from protflow.utils.seq_parser import parse_genbank

# Notebook 工具
from protflow.utils.notebook_utils import (
    check_and_install_packages,
    ensure_conda_env
)
```

## 更多信息

- **完整文档**: `docs/notebook-migration-guide.md`
- **Notebooks 指南**: `notebooks/README.md`
- **实施详情**: `docs/NOTEBOOK_OPTIMIZATION_SUMMARY.md`
- **示例**: `notebooks/EXAMPLE_NEW_NOTEBOOK.ipynb`

## 问题？

查看 `notebooks/README.md` 的故障排除部分，或查看示例 notebook。

---

**总结**: Notebooks 现在更简洁、更易于使用和维护！🚀
