#!/bin/bash
# ESM3 模型打包脚本
# 用于将本地下载的 ESM3 模型打包，准备传输到服务器

set -e  # 遇到错误立即退出

echo "=========================================="
echo "ESM3 模型打包工具"
echo "=========================================="

# 检查模型是否存在
MODEL_DIR="$HOME/.cache/huggingface/hub/models--EvolutionaryScale--esm3-sm-open-v1"
if [ ! -d "$MODEL_DIR" ]; then
    echo "❌ 错误: 未找到 ESM3 模型"
    echo "   路径: $MODEL_DIR"
    echo ""
    echo "请先下载模型："
    echo "  pip install esm huggingface_hub torch"
    echo "  huggingface-cli login"
    echo "  python -c \"from esm.models.esm3 import ESM3; ESM3.from_pretrained('esm3-sm-open-v1')\""
    exit 1
fi

echo "✅ 找到 ESM3 模型: $MODEL_DIR"
echo ""

# 显示模型大小
echo "📊 模型大小:"
du -sh "$MODEL_DIR"
echo ""

# 选择打包方式
echo "选择打包方式:"
echo "  1) 打包整个 huggingface 目录（推荐，约 1.5GB）"
echo "  2) 只打包 ESM3 模型（较小，约 1.4GB）"
echo ""
read -p "请选择 [1/2]: " choice

OUTPUT_DIR="$HOME"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

case $choice in
    1)
        echo ""
        echo "📦 打包整个 huggingface 目录..."
        cd "$HOME/.cache"
        OUTPUT_FILE="$OUTPUT_DIR/esm3_huggingface_$TIMESTAMP.tar.gz"
        tar -czf "$OUTPUT_FILE" huggingface/
        ;;
    2)
        echo ""
        echo "📦 只打包 ESM3 模型..."
        cd "$HOME/.cache/huggingface/hub"
        OUTPUT_FILE="$OUTPUT_DIR/esm3_model_$TIMESTAMP.tar.gz"
        tar -czf "$OUTPUT_FILE" models--EvolutionaryScale--esm3-sm-open-v1/
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "✅ 打包完成!"
echo ""
echo "📁 压缩包位置: $OUTPUT_FILE"
echo "📊 文件大小:"
ls -lh "$OUTPUT_FILE"
echo ""
echo "=========================================="
echo "下一步操作："
echo "=========================================="
echo ""
echo "1. 传输到服务器（选择一种方法）："
echo ""
echo "   方法 A - 使用 scp:"
echo "   scp $OUTPUT_FILE username@服务器地址:/tmp/"
echo ""
echo "   方法 B - 使用 rsync (支持断点续传):"
echo "   rsync -avz --progress $OUTPUT_FILE username@服务器地址:/tmp/"
echo ""
echo "   方法 C - JupyterLab 网页上传:"
echo "   在 JupyterLab 界面上传此文件"
echo ""
echo "2. 在服务器上解压："
echo ""
if [ "$choice" = "1" ]; then
    echo "   cd ~/.cache"
    echo "   tar -xzf /tmp/$(basename $OUTPUT_FILE)"
else
    echo "   mkdir -p ~/.cache/huggingface/hub"
    echo "   cd ~/.cache/huggingface/hub"
    echo "   tar -xzf /tmp/$(basename $OUTPUT_FILE)"
fi
echo ""
echo "3. 验证："
echo "   ls -lh ~/.cache/huggingface/hub/models--EvolutionaryScale--esm3-sm-open-v1/"
echo ""
echo "=========================================="

