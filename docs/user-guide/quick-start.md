# ProtFlow 快速开始指南

## 🎯 5分钟上手

### 步骤1: 环境检查
```bash
# 检查CUDA
nvidia-smi
nvcc --version  # 确认CUDA 13.0+

# 检查Python
python3 --version  # 确认3.8+
```

### 步骤2: 一键安装
```bash
# 克隆并进入项目
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# 运行自动安装脚本
chmod +x scripts/install_server.sh
./scripts/install_server.sh
```

### 步骤3: 基础配置
```bash
# 设置HuggingFace令牌（必需）
export HF_TOKEN=your_token_here

# 可选: 调整GPU设置
export CUDA_VISIBLE_DEVICES=0
```

### 步骤4: 启动分析
```bash
# 启动JupyterLab
jupyter lab

# 在浏览器中打开:
# 1. notebooks/core/00_genome_annotation_to_structure.ipynb
# 2. 上传你的FNA文件
# 3. 按顺序运行所有cell
```

## 📁 文件放置指南

### 输入文件位置
```
data/
├── sequences/       # 蛋白质序列文件(.faa, .fa, .fasta)
├── genomes/        # 基因组文件(.fna, .fasta)
├── structures/     # 已知结构文件(.pdb)
└── annotations/    # 注释文件(.gbk, .gff)
```

### 输出文件位置
```
outputs/
├── predictions/    # ESM3预测结果
├── structures/     # 生成的PDB文件
├── logs/          # 运行日志
└── reports/       # 分析报告
```

## 🔧 常用命令

### 环境管理
```bash
# 激活环境
source protflow-env/bin/activate

# 更新包
pip install -r requirements.txt --upgrade

# 检查依赖
python src/scripts/check_deps.py
```

### 运行监控
```bash
# 查看GPU使用率
nvidia-smi -l 1

# 查看系统资源
top -u $USER

# 查看Jupyter日志
tail -f jupyter.log
```

## ⚡ 性能调优

### 小数据集 (<100序列)
```json
{
  "max_sequences": 100,
  "parallel_predictions": true,
  "max_workers": 4,
  "gpu_memory_fraction": 0.8
}
```

### 大数据集 (>1000序列)
```json
{
  "max_sequences": 1000,
  "parallel_predictions": true,
  "max_workers": 16,
  "gpu_memory_fraction": 0.9,
  "enable_cache": true,
  "batch_size": 32
}
```

## 🚨 常见问题快速解决

### 问题1: CUDA out of memory
```bash
# 立即解决
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# 长期解决: 修改配置
# 降低max_sequences到10
# 降低gpu_memory_fraction到0.6
```

### 问题2: 内核崩溃
```bash
# 重启Jupyter
pkill -f jupyter
jupyter lab

# 检查内存
free -h  # 确保有足够可用内存
```

### 问题3: 导入错误
```bash
# 重新安装核心包
pip install --force-reinstall torch torchvision
pip install --force-reinstall biopython

# 检查Python路径
python -c "import sys; print(sys.path)"
```

## 📊 预期运行时间

| 数据规模 | 工作流程 | 预估时间 |
|---------|----------|----------|
| 50序列 | 结构预测 | 30分钟 |
| 50序列 | 完整流程 | 2小时 |
| 200序列 | 结构预测 | 2小时 |
| 200序列 | 完整流程 | 8小时 |
| 1000序列 | 批量分析 | 24小时 |

## 🎯 下一步

1. **完成首次运行**: 使用提供的测试数据
2. **调整参数**: 根据你的数据特点优化配置
3. **批量处理**: 设置自动化工作流
4. **结果分析**: 使用分析工具深入挖掘数据

---

**💡 提示**: 首次使用时建议先用小数据集测试，确认一切正常后再处理大规模数据！