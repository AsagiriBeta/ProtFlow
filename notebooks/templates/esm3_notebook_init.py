"""
ESM3 Notebook Initialization Template

This cell should be placed at the beginning of notebooks that use ESM3.
It will:
1. Add protflow to Python path
2. Setup the environment and paths
3. Check and install ESM3 dependencies
4. Import common modules

Usage: Copy this entire cell to your notebook.
"""

import sys
from pathlib import Path

# 1. Add protflow to path
project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:
    project_root = project_root.parent

if (project_root / 'src').exists():
    src_dir = str(project_root / 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    print(f"✓ protflow 路径: {src_dir}")
else:
    print("⚠ 警告: 未找到 protflow 源代码目录")

# 2. Import notebook utilities
from protflow.utils.notebook_utils import (
    setup_esm3_notebook,
)

# 3. Setup environment (automatically checks and installs dependencies)
# Customize work_dir_name for your notebook
paths = setup_esm3_notebook(work_dir_name='esm3_runs')

# 4. Common imports for ESM3 notebooks
import torch
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm

# Store important paths as variables
PROJECT_ROOT = paths['PROJECT_ROOT']
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

print(f"\n✓ 初始化完成")
print(f"  工作目录: {WORK_DIR}")
