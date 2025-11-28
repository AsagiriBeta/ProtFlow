# ProtFlow 安装指南

## 🎯 概述

本指南将帮助您在不同环境中安装和配置ProtFlow。

## 📋 系统要求

### 硬件要求
- **内存**: 最少16GB，推荐32GB或更高
- **存储**: 最少50GB可用空间，推荐100GB+ SSD
- **GPU**: NVIDIA GPU，推荐RTX 4090或A100（可选但强烈推荐）

### 软件要求
- **操作系统**: Linux (推荐Ubuntu 20.04+), macOS, 或 Windows (WSL2)
- **Python**: 3.8 或更高版本
- **CUDA**: 11.8+ 或 13.0+ (如果使用GPU)

## 🚀 快速安装

### 1. 克隆仓库
```bash
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow
```

### 2. 创建虚拟环境
```bash
# 使用venv
python3 -m venv protflow-env
source protflow-env/bin/activate  # Linux/Mac
# 或
protflow-env\\Scripts\\activate  # Windows

# 或使用conda
conda create -n protflow python=3.10
conda activate protflow
```

### 3. 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 验证安装
```bash
python -c "import protflow; print('ProtFlow installed successfully!')"
```

## ⚙️ 详细配置

### 环境变量设置
```bash
# 必需：HuggingFace Token
export HF_TOKEN=your_huggingface_token_here

# 可选：基础目录
export PROTFLOW_BASE_DIR=/path/to/your/output/directory

# 可选：GPU设置
export CUDA_VISIBLE_DEVICES=0  # 使用第一个GPU
```

### 配置文件
```bash
# 复制示例配置
cp config/config.example.json config/config.json

# 编辑配置
nano config/config.json
```

## 🔧 系统依赖安装

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y openjdk-11-jre openbabel autodock-vina
```

### macOS
```bash
# 使用Homebrew
brew install openjdk open-babel autodock-vina
```

### 可选工具
```bash
# Prokka (基因组注释)
conda create -n prokka -c bioconda prokka
conda activate prokka
prokka --setupdb

# antiSMASH (生物合成基因簇分析)
conda create -n antismash -c bioconda antismash
conda activate antismash
download-antismash-databases
```

## 🎯 环境特定安装

### 服务器环境
参考[服务器部署指南](../tools/deployment.md)了解详细的CUDA配置和性能优化。

### JupyterLab环境
```bash
pip install jupyter jupyterlab
jupyter lab --generate-config
```

### Docker环境
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
```

## ✅ 安装验证

### 基础验证
```bash
# 检查Python版本
python --version

# 检查关键依赖
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import protflow; print('✅ ProtFlow package imported successfully')"
```

### GPU验证（如果适用）
```bash
# 检查CUDA
nvidia-smi

# 检查PyTorch CUDA支持
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 工具验证
```bash
# 检查系统工具
java -version
obabel --version
vina --help
```

## 🚨 常见问题

### 问题1: CUDA版本不匹配
**症状**: `RuntimeError: CUDA error: no kernel image is available`
**解决**:
```bash
# 重新安装匹配的PyTorch版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 问题2: 内存不足
**症状**: `RuntimeError: CUDA out of memory`
**解决**: 修改配置文件，减少批处理大小：
```json
{
  "max_sequences": 5,
  "gpu_memory_fraction": 0.6,
  "batch_size": 1
}
```

### 问题3: 权限错误
**症状**: `Permission denied` 错误
**解决**:
```bash
# 确保有执行权限
chmod +x scripts/*.sh
# 或使用sudo（不推荐长期使用）
sudo python -m scripts.runner --help
```

## 🔍 下一步

安装完成后，您可以：
1. 查看[快速开始指南](quick-start.md)进行第一次分析
2. 浏览[Notebook使用指南](migration/notebook-usage.md)了解工作流程
3. 参考[配置文档](../configuration/overview.md)进行高级设置

## 🆘 获取帮助

如果遇到安装问题：
1. 查看[故障排除指南](tutorial/troubleshooting.md)
2. 检查[GitHub Issues](https://github.com/AsagiriBeta/ProtFlow/issues)
3. 确保系统满足所有要求
4. 尝试在干净的虚拟环境中重新安装

---

**💡 提示**: 建议在安装完成后先运行一个小型测试数据集，确保所有组件都正常工作。