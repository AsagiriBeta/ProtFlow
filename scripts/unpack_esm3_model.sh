#!/bin/bash
# ESM3 模型解压脚本（服务器端）
# 在服务器上运行此脚本来解压和验证模型

set -e

echo "=========================================="
echo "ESM3 模型解压工具（服务器端）"
echo "=========================================="

# 查找压缩包
echo ""
echo "🔍 查找上传的压缩包..."
echo ""

SEARCH_PATHS=("/tmp" "$HOME" "$HOME/Downloads")
FOUND_FILES=()

for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        while IFS= read -r file; do
            FOUND_FILES+=("$file")
        done < <(find "$path" -maxdepth 1 -name "esm3*.tar.gz" 2>/dev/null)
    fi
done

if [ ${#FOUND_FILES[@]} -eq 0 ]; then
    echo "❌ 未找到 ESM3 压缩包"
    echo ""
    echo "请先上传压缩包到以下位置之一："
    echo "  - /tmp/"
    echo "  - $HOME/"
    echo "  - $HOME/Downloads/"
    exit 1
fi

echo "找到以下压缩包:"
echo ""
for i in "${!FOUND_FILES[@]}"; do
    echo "  $((i+1))) ${FOUND_FILES[$i]}"
    ls -lh "${FOUND_FILES[$i]}"
done

echo ""
read -p "请选择要解压的文件 [1-${#FOUND_FILES[@]}]: " choice

if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#FOUND_FILES[@]} ]; then
    echo "❌ 无效选择"
    exit 1
fi

TAR_FILE="${FOUND_FILES[$((choice-1))]}"
echo ""
echo "✅ 选择了: $TAR_FILE"

# 确定解压方式
if [[ "$TAR_FILE" == *"huggingface"* ]]; then
    UNPACK_TYPE="full"
    TARGET_DIR="$HOME/.cache"
else
    UNPACK_TYPE="model_only"
    TARGET_DIR="$HOME/.cache/huggingface/hub"
fi

echo ""
echo "📦 准备解压..."
echo "   类型: $([[ "$UNPACK_TYPE" == "full" ]] && echo "完整 huggingface 目录" || echo "仅 ESM3 模型")"
echo "   目标: $TARGET_DIR"
echo ""
read -p "继续? [y/N]: " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 解压
echo ""
echo "📂 解压中..."
cd "$TARGET_DIR"
tar -xzf "$TAR_FILE" --checkpoint=.1000

echo ""
echo "✅ 解压完成!"

# 验证
echo ""
echo "🔍 验证模型文件..."

# 检查两个可能的位置
HF_MODEL_PATH="$HOME/.cache/huggingface/hub/models--EvolutionaryScale--esm3-sm-open-v1"
ESM3_MODEL_PATH="$HOME/.cache/esm3"

MODEL_FOUND=false

# 检查 huggingface 位置
if [ -d "$HF_MODEL_PATH" ]; then
    echo "✅ 模型目录存在: $HF_MODEL_PATH"
    echo ""
    echo "📊 模型大小:"
    du -sh "$HF_MODEL_PATH"
    MODEL_FOUND=true
    FINAL_PATH="$HF_MODEL_PATH"
fi

# 检查 esm3 位置
if [ -d "$ESM3_MODEL_PATH" ] && [ "$MODEL_FOUND" = false ]; then
    echo "✅ 模型目录存在: $ESM3_MODEL_PATH"
    echo ""
    echo "📊 模型大小:"
    du -sh "$ESM3_MODEL_PATH"
    MODEL_FOUND=true
    FINAL_PATH="$ESM3_MODEL_PATH"
fi

if [ "$MODEL_FOUND" = true ]; then
    echo ""
    echo "📁 关键文件:"
    find "$FINAL_PATH" -type f \( -name "*.safetensors" -o -name "config.json" \) | head -5

    # 检查关键文件
    if find "$FINAL_PATH" -name "*.safetensors" | grep -q .; then
        echo ""
        echo "✅ 找到模型权重文件 (.safetensors)"
    else
        echo ""
        echo "⚠️ 警告: 未找到 .safetensors 文件"
    fi

    if find "$FINAL_PATH" -name "config.json" | grep -q .; then
        echo "✅ 找到配置文件 (config.json)"
    else
        echo "⚠️ 警告: 未找到 config.json 文件"
    fi
else
    echo "❌ 错误: 模型目录不存在"
    echo "   检查了以下位置:"
    echo "   - $HF_MODEL_PATH"
    echo "   - $ESM3_MODEL_PATH"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 模型准备完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "  1. 打开 ESM3_Workflow.ipynb"
echo "  2. 运行第 3 步（检查模型缓存）"
echo "  3. 应该看到: ✅ 模型已缓存"
echo ""

# 清理询问
echo "是否删除压缩包以节省空间? [y/N]: "
read -p "" cleanup

if [[ "$cleanup" =~ ^[Yy]$ ]]; then
    rm -f "$TAR_FILE"
    echo "✅ 已删除: $TAR_FILE"
fi

echo ""
echo "完成！"

