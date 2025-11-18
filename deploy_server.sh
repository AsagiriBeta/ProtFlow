#!/bin/bash
# 服务器快速部署脚本
# 用于在远程服务器上快速配置 ProtFlow JupyterLab 环境

echo "========================================"
echo "  ProtFlow 服务器快速部署"
echo "========================================"
echo ""

# 检查必要命令
command -v python3 >/dev/null 2>&1 || { echo "❌ 需要 python3"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ 需要 git"; exit 1; }

# 1. 克隆或更新代码
if [ -d "ProtFlow" ]; then
    echo "📦 更新代码..."
    cd ProtFlow
    git pull
else
    echo "📦 克隆仓库..."
    git clone https://github.com/AsagiriBeta/ProtFlow.git
    cd ProtFlow
fi

# 2. 检测虚拟环境
VENV_CANDIDATES=(
    "$VIRTUAL_ENV"
    "$HOME/jupyter-env-3.12"
    "$HOME/venv"
    "$HOME/.venv"
)

VENV_PATH=""
for path in "${VENV_CANDIDATES[@]}"; do
    if [ -n "$path" ] && [ -d "$path" ]; then
        VENV_PATH="$path"
        break
    fi
done

if [ -z "$VENV_PATH" ]; then
    echo "⚠️  未检测到虚拟环境"
    read -p "请输入虚拟环境路径（或按 Enter 创建新的）: " USER_VENV

    if [ -z "$USER_VENV" ]; then
        VENV_PATH="$HOME/protflow-venv"
        echo "📦 创建新虚拟环境: $VENV_PATH"
        python3 -m venv "$VENV_PATH"
    else
        VENV_PATH="$USER_VENV"
    fi
fi

echo "✓ 使用虚拟环境: $VENV_PATH"
echo ""

# 3. 配置 CUDA（如果有 GPU）
if command -v nvidia-smi >/dev/null 2>&1; then
    echo "🎮 检测到 NVIDIA GPU"

    if [ -f "setup_cuda_env.sh" ]; then
        echo "🔧 配置 CUDA 环境..."
        chmod +x setup_cuda_env.sh
        ./setup_cuda_env.sh "$VENV_PATH"
    else
        echo "⚠️  未找到 setup_cuda_env.sh，跳过 CUDA 配置"
    fi
else
    echo "ℹ️  未检测到 GPU，跳过 CUDA 配置"
fi

echo ""

# 4. 安装依赖
echo "📦 安装依赖..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
pip install jupyter jupyterlab

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "启动 JupyterLab:"
echo "  source $VENV_PATH/bin/activate"
echo "  jupyter lab --ip=0.0.0.0 --port=8888 --no-browser"
echo ""
echo "或后台运行:"
echo "  nohup jupyter lab --ip=0.0.0.0 --port=8888 --no-browser > jupyter.log 2>&1 &"
echo ""
echo "访问:"
echo "  http://your-server-ip:8888"
echo ""

