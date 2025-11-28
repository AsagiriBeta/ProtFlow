# 从Colab到服务器迁移指南

## 🔄 主要变化对比

| 功能 | Colab版本 | 服务器版本 |
|------|-----------|------------|
| 环境 | 临时环境 | 永久环境 |
| 文件存储 | Google Drive | 本地文件系统 |
| GPU访问 | 自动配置 | 手动配置CUDA |
| 持久化 | 会话结束即丢失 | 数据永久保存 |
| 并行处理 | 有限支持 | 完全支持 |
| 批量处理 | 受限 | 大规模支持 |

## 📦 数据迁移

### 1. Colab数据导出
在Colab中运行：
```python
# 打包所有文件
!zip -r colab_data.zip /content/

# 下载到本地
from google.colab import files
files.download('colab_data.zip')
```

### 2. 数据上传到服务器
```bash
# 使用scp上传
scp colab_data.zip user@your-server:/path/to/ProtFlow/

# 解压数据
unzip colab_data.zip -d migration_data/
```

### 3. 数据重组织
```bash
# 创建目录结构
mkdir -p data/{sequences,genomes,structures,annotations}

# 移动文件到正确位置
mv migration_data/*.fna data/genomes/
mv migration_data/*.faa data/sequences/
mv migration_data/*.pdb data/structures/
mv migration_data/*.gbk data/annotations/
```

## 🔧 配置迁移

### Colab配置转换
Colab中的设置：
```python
# Colab设置
WORK_DIR = '/content/protflow'
HF_TOKEN = 'your_token'
LIMIT = 50
```

转换为服务器配置：
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "max_sequences": 50,
  "hf_token_env": "HF_TOKEN"
}
```

### 环境变量设置
```bash
# 设置环境变量（添加到~/.bashrc）
export HF_TOKEN=your_token_here
export PROTFLOW_BASE_DIR=/path/to/ProtFlow/outputs
export CUDA_VISIBLE_DEVICES=0
```

## 📝 Notebook修改要点

### 删除Colab特定代码
```python
# 删除这些Colab特定代码
from google.colab import files
from google.colab import drive
drive.mount('/content/drive')
```

### 更新文件路径
```python
# Colab路径
input_file = '/content/drive/MyDrive/data/protein.faa'

# 服务器路径
input_file = './data/sequences/protein.faa'
```

### 更新输出路径
```python
# Colab输出
output_dir = '/content/results'

# 服务器输出
output_dir = './outputs/predictions'
```

## ⚙️ 功能增强

### 1. 批量处理
服务器版本支持真正的批量处理：
```python
# 一次性处理整个目录
input_dir = './data/sequences/'
output_dir = './outputs/predictions/'

# 处理所有.faa文件
for file in Path(input_dir).glob('*.faa'):
    process_file(file, output_dir)
```

### 2. 并行处理
```json
{
  "parallel_predictions": true,
  "max_workers": 8,
  "batch_size": 16
}
```

### 3. 自动化工作流
```bash
# 创建自动化脚本
#!/bin/bash
# auto_analysis.sh

# 1. 基因组注释
jupyter nbconvert --to notebook --execute notebooks/tools/10_genome_annotation_prokka.ipynb

# 2. 结构预测
jupyter nbconvert --to notebook --execute notebooks/core/01_protein_structure_prediction.ipynb

# 3. 结果分析
jupyter nbconvert --to notebook --execute notebooks/analysis/20_cds_annotation_comparison.ipynb
```

## 🔍 验证迁移

### 1. 环境验证
```bash
# 运行环境检查
python tests/integration/check_environment.py

# 检查GPU
python -c "import torch; print(f'GPU可用: {torch.cuda.is_available()}')"
```

### 2. 功能验证
```bash
# 运行快速测试
python tests/integration/quick_test.py

# 验证特定功能
python tests/integration/test_prokka_setup.py
```

### 3. 结果对比
```python
# 比较Colab和服务器结果
import pandas as pd

colab_results = pd.read_csv('colab_results.csv')
server_results = pd.read_csv('server_results.csv')

# 检查关键指标是否一致
print("结果差异:", (colab_results - server_results).abs().max())
```

## 🚨 常见问题解决

### 问题1: 结果不一致
**原因**: 随机种子或精度差异
**解决**: 
```python
# 设置随机种子
import torch
import numpy as np
torch.manual_seed(42)
np.random.seed(42)
```

### 问题2: 内存错误
**原因**: 服务器内存限制
**解决**:
```json
{
  "max_sequences": 25,  // 减少序列数
  "gpu_memory_fraction": 0.6,  // 降低GPU内存使用
  "batch_size": 8  // 减小批大小
}
```

### 问题3: 路径错误
**原因**: 路径格式差异
**解决**:
```python
# 使用Path处理路径
from pathlib import Path
input_path = Path('./data/sequences') / 'protein.faa'
```

## 📈 性能提升

### Colab vs 服务器性能对比
| 配置 | Colab (免费) | 服务器 (RTX 4090) |
|------|-------------|------------------|
| GPU显存 | 15GB | 24GB |
| 内存 | 12GB | 64GB |
| 存储 | 临时 | NVMe SSD |
| 运行时间 | 100% | 40% |
| 并发处理 | 1个 | 8个 |

### 优化建议
1. **增加批处理大小** - 利用更大GPU显存
2. **启用并行处理** - 利用多核CPU
3. **使用SSD存储** - 加速I/O操作
4. **增加内存** - 处理更大数据集

## 🎯 最佳实践

### 1. 项目管理
```
project/
├── data/
│   ├── raw/          # 原始数据
│   ├── processed/    # 处理后的数据
│   └── results/      # 中间结果
├── notebooks/
├── outputs/
└── scripts/          # 自动化脚本
```

### 2. 版本控制
```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial migration from Colab"

# 定期提交
git add outputs/
git commit -m "Add analysis results $(date +%Y%m%d)"
```

### 3. 备份策略
```bash
# 自动备份脚本
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d)
tar -czf backup_${DATE}.tar.gz data/ outputs/ config/
rsync -av --delete . backup-server:/backups/protflow/
```

---

**🎉 恭喜！** 现在你已成功将ProtFlow从Colab迁移到自己的服务器，可以享受更强大的分析能力了！