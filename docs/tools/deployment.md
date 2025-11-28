# ProtFlow 部署指南

## 🎯 概述

本指南介绍如何在不同类型的服务器环境中部署ProtFlow，包括CUDA配置、性能优化和生产环境设置。

## 📋 部署要求

### 硬件要求
- **CPU**: 16核+ (推荐AMD EPYC或Intel Xeon)
- **内存**: 64GB+ DDR4
- **GPU**: NVIDIA RTX 4090或A100 (24GB+显存)
- **存储**: NVMe SSD 1TB+
- **网络**: 千兆网络连接

### 软件要求
- **操作系统**: Ubuntu 20.04 LTS或更高版本
- **CUDA**: 13.0+
- **Python**: 3.8+
- **Docker**: (可选，用于容器化部署)

## 🚀 快速部署

### 使用自动化脚本

我们提供了一个自动化部署脚本，可以快速配置服务器环境：

```bash
# 下载并运行部署脚本
curl -O https://raw.githubusercontent.com/AsagiriBeta/ProtFlow/main/docs/deploy_server.sh
chmod +x deploy_server.sh
./deploy_server.sh
```

脚本功能：
- ✅ 自动检测和配置虚拟环境
- ✅ CUDA环境设置
- ✅ 依赖项安装
- ✅ JupyterLab配置

### 手动部署步骤

#### 1. 系统准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget build-essential

# 安装CUDA 13 (如果尚未安装)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/13.0.0/local_installers/cuda-repo-ubuntu2004-13-0-local_13.0.0-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-13-0-local_13.0.0-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-13-0-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda
```

#### 2. 创建专用用户
```bash
# 创建protflow用户
sudo useradd -m -s /bin/bash protflow
sudo usermod -aG sudo protflow

# 切换到protflow用户
sudo su - protflow
```

#### 3. 安装ProtFlow
```bash
# 克隆仓库
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# 创建虚拟环境
python3 -m venv protflow-env
source protflow-env/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install jupyter jupyterlab

# 验证安装
python -c "import protflow; print('✅ ProtFlow installed successfully')"
```

#### 4. CUDA环境配置
```bash
# 创建CUDA配置脚本
cat > setup_cuda_env.sh << 'EOF'
#!/bin/bash
# CUDA环境设置脚本

VENV_PATH=$1
if [ -z "$VENV_PATH" ]; then
    echo "用法: $0 <虚拟环境路径>"
    exit 1
fi

# 设置CUDA路径
export CUDA_HOME=/usr/local/cuda-13.0
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# 激活虚拟环境
source $VENV_PATH/bin/activate

# 安装CUDA支持的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# 验证CUDA可用性
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
echo "✅ CUDA环境配置完成"
EOF

chmod +x setup_cuda_env.sh
./setup_cuda_env.sh protflow-env
```

## ⚙️ 生产环境配置

### Nginx反向代理
```nginx
# /etc/nginx/sites-available/protflow
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /static {
        alias /home/protflow/ProtFlow/static;
    }
}
```

### Systemd服务
```ini
# /etc/systemd/system/protflow.service
[Unit]
Description=ProtFlow JupyterLab Service
After=network.target

[Service]
Type=simple
User=protflow
WorkingDirectory=/home/protflow/ProtFlow
Environment=PATH=/home/protflow/ProtFlow/protflow-env/bin:/usr/local/cuda-13.0/bin:/usr/bin:/bin
Environment=CUDA_HOME=/usr/local/cuda-13.0
Environment=LD_LIBRARY_PATH=/usr/local/cuda-13.0/lib64
ExecStart=/home/protflow/ProtFlow/protflow-env/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.password=''
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 启用服务
```bash
sudo systemctl enable protflow
sudo systemctl start protflow
sudo systemctl status protflow
```

## 🔧 性能优化

### CUDA优化
```bash
# 创建CUDA优化配置
cat > cuda_optimization.conf << 'EOF'
# CUDA优化设置
export CUDA_CACHE_MAXSIZE=2147483647
export CUDA_CACHE_PATH=/home/protflow/.cuda_cache
export CUDA_VISIBLE_DEVICES=0

# PyTorch CUDA优化
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
EOF

# 添加到环境
echo "source /home/protflow/cuda_optimization.conf" >> ~/.bashrc
```

### 内存管理
```json
// config/server-config.json
{
  "gpu_memory_fraction": 0.9,
  "max_ram_usage_gb": 56,
  "enable_cache": true,
  "cache_size_limit_gb": 10,
  "parallel_predictions": true,
  "max_workers": 16,
  "batch_size": 32
}
```

### JupyterLab优化
```python
# ~/.jupyter/jupyter_lab_config.py
c.ServerApp.max_buffer_size = 2147483647
c.ServerApp.max_body_size = 2147483647
c.ServerApp.max_header_size = 2147483647
c.ServerApp.timeout = 3600
c.ServerApp.shutdown_no_activity_timeout = 3600
```

## 🐳 Docker部署

### Dockerfile
```dockerfile
FROM nvidia/cuda:13.0-devel-ubuntu20.04

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 python3-pip git \
    openjdk-11-jre openbabel \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install jupyter jupyterlab

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  protflow:
    build: .
    ports:
      - "8888:8888"
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
      - ./notebooks:/app/notebooks
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 🔒 安全配置

### 防火墙设置
```bash
# UFW防火墙
sudo ufw allow 8888/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 8888 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

### SSL证书
```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 访问控制
```python
# JupyterLab配置
# ~/.jupyter/jupyter_lab_config.py
c.ServerApp.token = 'your-secure-token'
c.ServerApp.password = 'sha1:your-hashed-password'
c.ServerApp.allow_origin = 'your-domain.com'
```

## 📊 监控和日志

### 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# GPU监控
nvidia-smi -l 1  # 每秒更新
nvidia-smi dmon  # 详细监控
```

### 日志管理
```bash
# 创建日志目录
mkdir -p /var/log/protflow

# 日志轮转配置
sudo tee /etc/logrotate.d/protflow << 'EOF'
/var/log/protflow/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 protflow protflow
}
EOF
```

## 🔄 更新和维护

### 代码更新
```bash
# 停止服务
sudo systemctl stop protflow

# 更新代码
cd /home/protflow/ProtFlow
git pull

# 更新依赖
source protflow-env/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl start protflow
```

### 系统更新
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 更新CUDA（谨慎操作）
# 参考NVIDIA官方文档
```

## 🆘 故障排除

### 服务无法启动
```bash
# 检查日志
sudo journalctl -u protflow -f

# 检查端口占用
sudo netstat -tlnp | grep 8888

# 检查依赖
python -c "import protflow; print('✅ OK')"
```

### GPU不可用
```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查CUDA
nvcc --version

# 检查PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### 内存不足
```bash
# 检查内存使用
free -h

# 检查GPU内存
nvidia-smi

# 调整配置
# 编辑config/config.json，减少max_sequences
```

## 📈 性能基准

### 期望性能
| 硬件配置 | 50序列 | 200序列 | 1000序列 |
|----------|--------|---------|----------|
| RTX 4090 | 30分钟 | 2小时 | 8小时 |
| A100 40GB | 20分钟 | 1.5小时 | 6小时 |
| 多GPU配置 | 15分钟 | 1小时 | 4小时 |

## 🔍 相关文档

- [安装指南](../user-guide/installation.md) - 详细安装步骤
- [配置参考](../configuration/overview.md) - 配置选项说明
- [性能优化](../configuration/performance-tuning.md) - 性能调优指南

---

**💡 提示**: 部署完成后，建议先使用小数据集测试所有功能，确保系统配置正确。定期进行系统维护和更新，保持最佳性能。