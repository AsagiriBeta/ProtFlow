#!/usr/bin/env python3
"""
环境检查脚本 - 验证 Prokka-ESM3 工作流所需的依赖
"""

import sys
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python 版本过低: {version.major}.{version.minor}")
        print(f"    需要 Python 3.8 或更高版本")
        return False

def check_module(module_name, import_name=None, optional=False):
    """检查 Python 模块"""
    if import_name is None:
        import_name = module_name

    try:
        mod = __import__(import_name)
        version = getattr(mod, '__version__', 'unknown')
        status = "✓" if not optional else "✓ (可选)"
        print(f"  {status} {module_name}: {version}")
        return True
    except ImportError:
        status = "✗" if not optional else "○ (可选)"
        print(f"  {status} {module_name}: 未安装")
        return optional  # 可选模块返回 True

def check_command(cmd, name=None, optional=False):
    """检查命令行工具"""
    import subprocess
    if name is None:
        name = cmd

    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # 尝试提取版本号
            version_line = result.stdout.split('\n')[0] if result.stdout else result.stderr.split('\n')[0]
            status = "✓" if not optional else "✓ (可选)"
            print(f"  {status} {name}: {version_line[:60]}")
            return True
        else:
            raise FileNotFoundError
    except (FileNotFoundError, subprocess.TimeoutExpired):
        status = "✗" if not optional else "○ (可选)"
        print(f"  {status} {name}: 未找到")
        return optional

def check_gpu():
    """检查 GPU 可用性"""
    print("\n检查 GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"  ✓ CUDA 可用")
            print(f"    设备: {gpu_name}")
            print(f"    显存: {gpu_memory:.1f} GB")
            return True
        else:
            print(f"  ○ CUDA 不可用 (将使用 CPU)")
            return True  # CPU 也可以运行
    except ImportError:
        print(f"  ✗ PyTorch 未安装")
        return False

def check_disk_space():
    """检查磁盘空间"""
    print("\n检查磁盘空间...")
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)

        if free_gb >= 10:
            print(f"  ✓ 可用空间: {free_gb:.1f} GB")
            return True
        else:
            print(f"  ⚠ 可用空间较少: {free_gb:.1f} GB")
            print(f"    建议至少 10 GB 空闲空间")
            return True  # 警告但不阻止
    except Exception as e:
        print(f"  ○ 无法检查磁盘空间: {e}")
        return True

def main():
    """主检查函数"""
    print("="*60)
    print("Prokka-ESM3 工作流环境检查")
    print("="*60)

    all_ok = True

    # 1. Python 版本
    all_ok &= check_python_version()

    # 2. 核心 Python 模块
    print("\n检查核心 Python 包...")
    all_ok &= check_module('torch', 'torch')
    all_ok &= check_module('biopython', 'Bio')
    all_ok &= check_module('tqdm', 'tqdm')

    # 3. ESM 模块
    print("\n检查 ESM 包...")
    all_ok &= check_module('esm', 'esm')

    # 4. 可选 Python 模块
    print("\n检查可选 Python 包...")
    check_module('jupyter', 'jupyter', optional=True)
    check_module('notebook', 'notebook', optional=True)

    # 5. Prokka
    print("\n检查 Prokka...")
    prokka_ok = check_command('prokka', 'Prokka')
    all_ok &= prokka_ok

    if prokka_ok:
        # 检查 Prokka 数据库
        print("\n检查 Prokka 数据库...")
        check_command('prokka', 'Prokka --listdb', optional=True)

    # 6. GPU
    check_gpu()

    # 7. 磁盘空间
    check_disk_space()

    # 总结
    print("\n" + "="*60)
    if all_ok:
        print("✓ 环境检查通过！")
        print("\n你可以开始使用 Prokka-ESM3 工作流了。")
        print("\n下一步:")
        print("  1. 在 Colab 中打开 Prokka_ESM3_Workflow.ipynb")
        print("  2. 或在本地运行: jupyter notebook Prokka_ESM3_Workflow.ipynb")
    else:
        print("✗ 环境检查失败")
        print("\n需要安装缺失的依赖:")
        print("\n# 安装 Prokka (使用 mamba)")
        print("mamba install -c conda-forge -c bioconda -c defaults prokka")
        print("\n# 安装 Python 包")
        print("pip install esm biopython tqdm torch")
        print("\n# 如果需要 Jupyter")
        print("pip install jupyter notebook")
    print("="*60)

    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

