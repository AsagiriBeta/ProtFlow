# Notebook 模板

所有 notebooks 应遵循此模板，保持简洁，只包含前端调用代码。

## 标准结构

```python
# ============================================
# 1. 初始化（统一使用 init_notebook）
# ============================================

from protflow.utils.notebook_utils import init_notebook, ESM3_PACKAGES

# 自动检测环境、设置路径、安装依赖
paths = init_notebook('workflow_name', packages=ESM3_PACKAGES)
WORK_DIR = paths['WORK_DIR']
DATA_DIR = paths['DATA_DIR']

# ============================================
# 2. 导入后端模块（所有业务逻辑在后端）
# ============================================

from protflow.prediction.esm3_predict import (
    predict_structures_from_fasta,
    ESM3GenerationConfig
)

# ============================================
# 3. 配置参数
# ============================================

gen_config = ESM3GenerationConfig(
    track='structure',
    num_steps=8,
    temperature=None
)

# ============================================
# 4. 调用后端函数（简洁明了）
# ============================================

results = predict_structures_from_fasta(
    fasta_file=input_file,
    out_dir=WORK_DIR / 'outputs',
    generation_config=gen_config,
    min_seq_length=30,
    max_seq_length=2000,
    show_progress=True
)

# ============================================
# 5. 结果展示（可选）
# ============================================

print(f"成功: {results['success']}")
print(f"错误: {results['errors']}")
```

## 精简原则

### ✅ 应该做的

1. **使用统一初始化**：所有 notebooks 使用 `init_notebook()`
2. **调用后端模块**：所有功能从 `protflow.*` 导入
3. **保持简洁**：只包含必要的配置和调用
4. **清晰文档**：用 markdown 说明每个步骤

### ❌ 不应该做的

1. **不要重复实现**：业务逻辑应该在后端，不在 notebook 中
2. **不要手动设置路径**：使用 `init_notebook()` 自动处理
3. **不要手动安装依赖**：`init_notebook()` 会自动安装
4. **不要写长函数**：复杂逻辑应该在后端模块中

## 示例对比

### ❌ 旧方式（冗长、重复）

```python
# 手动设置路径
import sys
from pathlib import Path
project_root = Path.cwd()
while not (project_root / 'src' / 'protflow').exists():
    project_root = project_root.parent
sys.path.insert(0, str(project_root / 'src'))

# 手动安装依赖
import subprocess
subprocess.run([sys.executable, '-m', 'pip', 'install', 'esm', 'biopython'])

# 手动创建目录
WORK_DIR = Path('./outputs')
WORK_DIR.mkdir(exist_ok=True)

# 在 notebook 中实现业务逻辑
def predict_structure(sequence):
    # 大量业务逻辑代码...
    pass
```

### ✅ 新方式（简洁、统一）

```python
# 一行初始化
from protflow.utils.notebook_utils import init_notebook, ESM3_PACKAGES
paths = init_notebook('workflow', packages=ESM3_PACKAGES)
WORK_DIR = paths['WORK_DIR']

# 直接调用后端
from protflow.prediction.esm3_predict import predict_structures_from_fasta
results = predict_structures_from_fasta(...)
```

## 迁移步骤

将现有 notebook 迁移到新模板：

1. **替换初始化代码**
   - 删除手动路径设置
   - 删除手动依赖安装
   - 使用 `init_notebook()` 替换

2. **移除业务逻辑**
   - 将自定义函数移到 `src/protflow/` 相应模块
   - 在 notebook 中只保留调用

3. **简化导入**
   - 只导入需要的函数，不要导入整个模块

4. **更新文档**
   - 确保 markdown 单元格清晰说明每个步骤
