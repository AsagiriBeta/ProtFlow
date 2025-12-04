#!/usr/bin/env python3
"""Script to update notebooks to use shared utilities."""

import json
from pathlib import Path


ESM3_INIT_CELL = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# 环境设置与依赖检查\n",
        "import sys\n",
        "from pathlib import Path\n",
        "\n",
        "# Add protflow to path\n",
        "project_root = Path.cwd()\n",
        "while not (project_root / 'src' / 'protflow').exists() and project_root != project_root.parent:\n",
        "    project_root = project_root.parent\n",
        "\n",
        "if (project_root / 'src').exists():\n",
        "    src_dir = str(project_root / 'src')\n",
        "    if src_dir not in sys.path:\n",
        "        sys.path.insert(0, src_dir)\n",
        "    print(f\"✓ protflow 路径: {src_dir}\")\n",
        "\n",
        "# Setup environment\n",
        "from protflow.utils.notebook_utils import setup_esm3_notebook\n",
        "paths = setup_esm3_notebook(work_dir_name='esm3_runs')\n",
        "\n",
        "# Common imports\n",
        "import torch\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "from tqdm import tqdm\n",
        "\n",
        "PROJECT_ROOT = paths['PROJECT_ROOT']\n",
        "WORK_DIR = paths['WORK_DIR']\n",
        "DATA_DIR = paths['DATA_DIR']\n",
        "\n",
        "print(f\"\\n✓ 初始化完成. 工作目录: {WORK_DIR}\")"
    ]
}

print("Update script placeholder - see templates/ directory for manual updates")
