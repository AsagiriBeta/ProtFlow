#!/usr/bin/env python3
"""
测试 Prokka 环境设置脚本
模拟 Notebook 第 2 步的行为
"""

import subprocess
import shutil
import os
from pathlib import Path

print("="*60)
print("测试 Prokka 环境设置")
print("="*60)

# 检测可用的 conda/mamba 包管理器
CONDA_BIN = None

# 首先检查 micromamba 和 mamba (更快)
for cmd in ['micromamba', 'mamba']:
    bin_path = shutil.which(cmd)
    if bin_path:
        CONDA_BIN = (cmd, bin_path)
        print(f"\n✅ 检测到 {cmd}: {bin_path}")
        break

# 如果没有，检查 conda
if not CONDA_BIN:
    # conda 通常是 shell 函数，需要特殊处理
    conda_exe = os.environ.get('CONDA_EXE') or shutil.which('conda')
    if conda_exe:
        CONDA_BIN = ('conda', conda_exe)
        print(f"\n✅ 检测到 conda: {conda_exe}")

if not CONDA_BIN:
    print("\n⚠️ 未检测到 conda/mamba/micromamba")
    print("请先安装 conda、mamba 或 micromamba")
    exit(1)

conda_cmd, conda_path = CONDA_BIN

# 检查 prokka 环境是否存在
print(f"\n检查 'prokka' 环境是否存在...")
try:
    env_list = subprocess.run(
        [conda_path, 'env', 'list'],
        capture_output=True,
        text=True,
        check=True
    )
    env_exists = 'prokka' in env_list.stdout

    if env_exists:
        print("✅ 发现已存在的 'prokka' 环境")

        # 测试 prokka 命令
        print("\n测试 Prokka 命令...")
        if conda_cmd == 'conda':
            test_cmd = ['conda', 'run', '-n', 'prokka', 'prokka', '--version']
        else:
            test_cmd = [conda_path, 'run', '-n', 'prokka', 'prokka', '--version']

        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True, check=True)
            print(f"✅ Prokka 版本: {result.stdout.strip()}")
            print("\n🎉 Prokka 已就绪，可以继续运行 Notebook！")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Prokka 命令测试失败: {e}")
            print("环境可能损坏，建议重新创建")
    else:
        print("ℹ️  'prokka' 环境不存在")
        print(f"\n将使用 {conda_cmd} 自动创建环境")
        print("这需要大约 5-10 分钟...")
        print("\n你可以:")
        print("  1. 直接重新运行 Notebook 第 2 步（自动创建）")
        print("  2. 或手动创建:")
        print(f"     {conda_cmd} create -n prokka -c conda-forge -c bioconda prokka")

except Exception as e:
    print(f"❌ 检查环境时出错: {e}")
    exit(1)

print("\n" + "="*60)
print("测试完成")
print("="*60)

