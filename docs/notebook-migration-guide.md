# 如何更新 Notebook 使用共享工具

本指南介绍如何更新现有的 Jupyter Notebook，使其使用新的共享工具和依赖管理系统。

## 概述

新的共享工具系统提供了：
- ✅ 自动依赖检查和安装
- ✅ 标准化的环境设置
- ✅ 减少代码重复
- ✅ 更容易维护

## 更新步骤

### 1. 识别需要替换的代码

查找并标记以下类型的代码单元格：

#### 需要删除的代码模式：

```python
# 手动包安装
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# 手动环境设置
PROJECT_ROOT = Path(os.environ.get('PROTFLOW_ROOT', Path.cwd())).resolve()
WORK_DIR = PROJECT_ROOT / 'some_runs'
WORK_DIR.mkdir(exist_ok=True, parents=True)

# 手动检查环境
IN_COLAB = 'google.colab' in sys.modules
IN_JUPYTERHUB = bool(os.environ.get('JUPYTERHUB_SERVICE_PREFIX'))
```

### 2. 根据 Notebook 类型选择初始化模板

#### 对于 ESM3 结构预测 Notebook

```python
# 环境设置与依赖检查
import sys
from pathlib import Path

# Add protflow to path
project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:
    project_root = project_root.parent

if (project_root / 'src').exists():
    src_dir = str(project_root / 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    print(f"✓ protflow 路径: {src_dir}")

# Setup environment (automatically checks and installs dependencies)
from protflow.utils.notebook_utils import setup_esm3_notebook

paths = setup_esm3_notebook(work_dir_name='esm3_runs')

# Common imports
import torch
import pandas as pd
import numpy as np
from tqdm import tqdm

# Store paths
PROJECT_ROOT = paths['PROJECT_ROOT']
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

print(f"\n✓ 初始化完成. 工作目录: {WORK_DIR}")
```

#### 对于分析和可视化 Notebook

```python
# 环境设置与依赖检查
import sys
from pathlib import Path

# Add protflow to path
project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:
    project_root = project_root.parent

if (project_root / 'src').exists():
    src_dir = str(project_root / 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    print(f"✓ protflow 路径: {src_dir}")

# Setup environment (automatically checks and installs dependencies)
from protflow.utils.notebook_utils import setup_analysis_notebook

paths = setup_analysis_notebook(work_dir_name='analysis_runs')

# Common imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# Store paths
PROJECT_ROOT = paths['PROJECT_ROOT']
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

print(f"\n✓ 初始化完成. 工作目录: {WORK_DIR}")
```

#### 对于使用 Conda 工具的 Notebook (Prokka, antiSMASH, DALI)

```python
# 环境设置与依赖检查
import sys
from pathlib import Path

# Add protflow to path
project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:
    project_root = project_root.parent

if (project_root / 'src').exists():
    src_dir = str(project_root / 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    print(f"✓ protflow 路径: {src_dir}")

# Import utilities
from protflow.utils.notebook_utils import (
    setup_notebook_environment,
    print_environment_info,
    check_and_install_packages,
    check_conda_environment,
    ensure_conda_env,
    CORE_PACKAGES
)

# Check Python dependencies
print("正在检查 Python 依赖...")
check_and_install_packages(CORE_PACKAGES)

# Setup environment
paths = setup_notebook_environment(work_dir_name='tool_runs')
print_environment_info(paths, verbose=False)

# Check for conda
conda_info = check_conda_environment()
if conda_info:
    conda_cmd, conda_path = conda_info
    print(f"\n✓ 检测到 {conda_cmd}: {conda_path}")

# Common imports
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

PROJECT_ROOT = paths['PROJECT_ROOT']
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

print(f"\n✓ 初始化完成. 工作目录: {WORK_DIR}")
```

### 3. 使用共享工具中的函数

#### 依赖管理

**旧代码：**
```python
try:
    import some_package
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "some_package"])
```

**新代码：**
```python
from protflow.utils.notebook_utils import check_and_install_packages
check_and_install_packages(['some_package', 'another_package'])
```

#### Conda 环境管理

**旧代码：**
```python
# Complex conda setup code...
```

**新代码：**
```python
from protflow.utils.notebook_utils import ensure_conda_env

# Ensure environment exists with required packages
cmd = ensure_conda_env(
    env_name='prokka',
    packages=['prokka'],
    auto_create=True
)

# Use the command
import subprocess
subprocess.run(cmd + ['prokka', '--version'])
```

### 4. 调用 src 中的代码

现在可以直接从 `protflow` 模块导入功能：

```python
# 结构预测
from protflow.prediction.esm3_predict import predict_structure

# 口袋检测
from protflow.docking.p2rank import detect_pockets

# 序列解析
from protflow.utils.seq_parser import parse_genbank, extract_sequences

# CDS 比较
from protflow.core.cds_comparison import compare_annotations
```

### 5. 测试更新后的 Notebook

1. 重启内核
2. 运行所有单元格
3. 验证：
   - 依赖自动安装
   - 路径正确设置
   - 所有功能正常工作

## 示例：更新前后对比

### 更新前 (多个单元格)

```python
# Cell 1: Environment setup
import sys
import os
from pathlib import Path
PROJECT_ROOT = Path(os.environ.get('PROTFLOW_ROOT', Path.cwd())).resolve()
WORK_DIR = PROJECT_ROOT / 'esm3_runs'
WORK_DIR.mkdir(exist_ok=True, parents=True)
```

```python
# Cell 2: Install packages
import subprocess
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = ["torch", "biopython", "tqdm"]
for pkg in packages:
    install_package(pkg)
```

```python
# Cell 3: Imports
import torch
import pandas as pd
from Bio import SeqIO
from tqdm import tqdm
```

### 更新后 (单个单元格)

```python
# 环境设置与依赖检查
import sys
from pathlib import Path

# Add protflow to path
project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:
    project_root = project_root.parent

if (project_root / 'src').exists():
    src_dir = str(project_root / 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# Setup environment (automatically checks and installs dependencies)
from protflow.utils.notebook_utils import setup_esm3_notebook
paths = setup_esm3_notebook(work_dir_name='esm3_runs')

# Common imports
import torch
import pandas as pd
from tqdm import tqdm

PROJECT_ROOT = paths['PROJECT_ROOT']
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

print(f"\n✓ 初始化完成. 工作目录: {WORK_DIR}")
```

## 可用的共享工具

### 包组

- `CORE_PACKAGES`: biopython, pandas, numpy, tqdm
- `ESM3_PACKAGES`: CORE_PACKAGES + esm, huggingface_hub, torch
- `VISUALIZATION_PACKAGES`: matplotlib, py3Dmol
- `NOTEBOOK_PACKAGES`: ipykernel

### 主要函数

- `check_and_install_packages(packages)`: 检查并安装包
- `setup_notebook_environment(work_dir_name)`: 设置环境
- `setup_esm3_notebook(work_dir_name)`: ESM3 特定设置
- `setup_analysis_notebook(work_dir_name)`: 分析特定设置
- `check_conda_environment()`: 检查 conda 是否可用
- `ensure_conda_env(env_name, packages)`: 确保 conda 环境存在
- `print_environment_info(paths)`: 打印环境信息

## 好处

1. **代码更少**：初始化从多个单元格减少到一个
2. **更容易维护**：更新一次，所有 notebook 受益
3. **更可靠**：经过测试的依赖管理
4. **更清晰**：标准化的结构和命名
5. **可重用**：可以在 notebook 之间共享代码

## 需要帮助？

查看以下文件：
- `notebooks/templates/` - 初始化模板
- `src/protflow/utils/notebook_utils.py` - 工具实现
- 已更新的示例 notebook
