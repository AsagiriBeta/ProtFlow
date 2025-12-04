"""
Conda Tool Notebook Initialization Template

This cell should be placed at the beginning of notebooks that use conda-based tools
(e.g., Prokka, antiSMASH, DALI).

It will:
1. Add protflow to Python path
2. Setup the environment and paths
3. Check for conda/mamba/micromamba
4. Import common modules

Usage: Copy this entire cell to your notebook and customize as needed.
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
    setup_notebook_environment,
    print_environment_info,
    check_and_install_packages,
    check_conda_environment,
    ensure_conda_env,
    CORE_PACKAGES
)

# 3. Check core Python dependencies
print("正在检查 Python 依赖...")
check_and_install_packages(CORE_PACKAGES)

# 4. Setup environment
paths = setup_notebook_environment(work_dir_name='tool_runs')
print_environment_info(paths, verbose=False)

# 5. Check for conda environment
conda_info = check_conda_environment()
if conda_info:
    conda_cmd, conda_path = conda_info
    print(f"\n✓ 检测到 {conda_cmd}: {conda_path}")
else:
    print("\n⚠ 未检测到 conda/mamba/micromamba")
    print("如需使用 conda 工具，请安装：")
    print("  - micromamba: https://mamba.readthedocs.io/en/latest/installation.html")
    print("  - conda: https://docs.conda.io/en/latest/miniconda.html")

# 6. Common imports
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

# CUSTOMIZE: Set tool-specific variables here
# Example:
# TOOL_NAME = 'prokka'
# TOOL_ENV_NAME = 'prokka'
# TOOL_PACKAGES = ['prokka']
