#!/usr/bin/env python3
"""
快速测试脚本 - 验证 Prokka-ESM3 工作流（使用示例数据）

这个脚本将使用项目中的示例 FNA 文件快速测试工作流。
适合用于验证环境配置是否正确。
"""

import sys
import shutil
from pathlib import Path

def print_banner(text):
    """打印横幅"""
    width = 60
    print("\n" + "="*width)
    print(text.center(width))
    print("="*width + "\n")

def quick_test():
    """快速测试函数"""

    print_banner("Prokka-ESM3 工作流快速测试")

    # 检查示例文件
    example_fna = Path(__file__).parent / "example_input.fna"
    if not example_fna.exists():
        print("❌ 错误: 找不到示例文件 example_input.fna")
        print("   请确保在 ProtFlow 项目目录中运行此脚本")
        return 1

    print(f"✓ 找到示例文件: {example_fna}")

    # 创建测试输出目录
    test_dir = Path("./test_output")
    if test_dir.exists():
        print(f"\n清理旧的测试输出...")
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    print(f"✓ 创建测试目录: {test_dir}\n")

    # 导入所需模块
    print("正在导入模块...")
    try:
        import torch
        from Bio import SeqIO
        print("✓ 核心模块导入成功\n")
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("\n请先安装依赖:")
        print("  pip install esm biopython tqdm torch")
        return 1

    # 这里可以添加实际的测试逻辑
    # 由于完整测试需要 Prokka 和 ESM3，这里只做基本验证

    print_banner("环境验证")

    # 检查 PyTorch
    print("PyTorch:")
    print(f"  版本: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    else:
        print(f"  GPU: 不可用 (将使用 CPU)")

    # 检查 Biopython
    import Bio
    print(f"\nBiopython:")
    print(f"  版本: {Bio.__version__}")

    # 验证示例文件可读取
    print(f"\n示例 FNA 文件:")
    records = list(SeqIO.parse(example_fna, "fasta"))
    print(f"  序列数量: {len(records)}")
    for i, rec in enumerate(records, 1):
        print(f"  {i}. {rec.id}: {len(rec.seq)} bp")

    print_banner("验证完成")

    print("✓ 基本环境验证通过！\n")
    print("下一步:")
    print("  1. 完整测试: 运行 Prokka_ESM3_Workflow.ipynb")
    print("  2. 环境检查: python check_environment.py")
    print("  3. 阅读文档: cat QUICKSTART.md")

    print("\n注意:")
    print("  - 完整工作流需要 Prokka 和 ESM3")
    print("  - 建议在 Google Colab 中运行以获得免费 GPU")
    print("  - 或按照 README.md 安装完整环境\n")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(quick_test())
    except KeyboardInterrupt:
        print("\n\n中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

