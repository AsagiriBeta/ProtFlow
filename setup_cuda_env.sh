#!/bin/bash
# CUDA 环境自动配置脚本 - 服务器端使用
# 用途：自动修改 venv 的 activate 脚本，添加 CUDA 环境变量
#
# 使用方法：
#   chmod +x setup_cuda_env.sh
#   ./setup_cuda_env.sh ~/jupyter-env-3.12

set -e

echo "======================================"
echo "  CUDA 环境配置脚本 for JupyterLab"
echo "======================================"
echo ""

# 检查参数
VENV_PATH="${1:-$VIRTUAL_ENV}"

if [ -z "$VENV_PATH" ]; then
    echo "❌ 错误: 请指定虚拟环境路径"
    echo ""
    echo "使用方法:"
    echo "  $0 /path/to/venv"
    echo ""
    echo "示例:"
    echo "  $0 ~/jupyter-env-3.12"
    exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ 错误: 虚拟环境路径不存在: $VENV_PATH"
    exit 1
fi

ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "❌ 错误: 未找到 activate 脚本: $ACTIVATE_SCRIPT"
    exit 1
fi

echo "虚拟环境: $VENV_PATH"
echo ""

# 查找 CUDA 安装路径
echo "🔍 查找 CUDA 安装..."
CUDA_LOCATIONS=(
    "/usr/local/cuda"
    "/usr/local/cuda-13.0"
    "/usr/local/cuda-12.0"
    "/usr/local/cuda-11.0"
    "/opt/cuda"
)

CUDA_HOME=""
for path in "${CUDA_LOCATIONS[@]}"; do
    if [ -d "$path" ] && [ -f "$path/bin/nvcc" ]; then
        CUDA_HOME="$path"
        break
    fi
done

if [ -z "$CUDA_HOME" ]; then
    echo "❌ 未找到 CUDA 安装"
    echo "请确保 CUDA 已安装，或手动指定 CUDA_HOME"
    exit 1
fi

echo "✓ 找到 CUDA: $CUDA_HOME"
echo ""

# 检查是否已配置
if grep -q "# CUDA Environment Configuration" "$ACTIVATE_SCRIPT"; then
    echo "⚠️  activate 脚本已包含 CUDA 配置"
    echo "如需重新配置，请先手动删除相关行"
    exit 0
fi

# 备份原始文件
BACKUP_FILE="${ACTIVATE_SCRIPT}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ACTIVATE_SCRIPT" "$BACKUP_FILE"
echo "✓ 已备份: $BACKUP_FILE"
echo ""

# 添加 CUDA 配置
echo "📝 添加 CUDA 环境变量到 activate 脚本..."

cat >> "$ACTIVATE_SCRIPT" << EOF

# CUDA Environment Configuration (Added by setup_cuda_env.sh)
export CUDA_HOME="$CUDA_HOME"
export CUDA_PATH="\$CUDA_HOME"
export PATH="\$CUDA_HOME/bin:\$PATH"
export LD_LIBRARY_PATH="\$CUDA_HOME/lib64:\${LD_LIBRARY_PATH}"
EOF

echo "✓ 配置已添加"
echo ""

# 验证
echo "🧪 验证配置..."
echo "---"
source "$ACTIVATE_SCRIPT"

echo "环境变量:"
echo "  CUDA_HOME=$CUDA_HOME"
echo "  PATH 包含 CUDA: $(echo $PATH | grep -o "$CUDA_HOME/bin" || echo "❌")"
echo ""

if command -v nvcc &> /dev/null; then
    echo "✓ nvcc 可用:"
    nvcc --version | head -n 4
else
    echo "❌ nvcc 仍不可用（可能需要重新激活虚拟环境）"
fi

echo ""
echo "======================================"
echo "✅ 配置完成！"
echo "======================================"
echo ""
echo "下一步："
echo "  1. 重启 JupyterLab:"
echo "     pkill -f jupyter"
echo "     source $VENV_PATH/bin/activate"
echo "     jupyter lab"
echo ""
echo "  2. 或者在当前 session 中:"
echo "     source $VENV_PATH/bin/activate"
echo "     nvcc -V  # 验证"
echo ""

