#!/usr/bin/env python3
"""
Prokka_ESM3_Workflow_JLab.ipynb 自动安装功能测试脚本

在服务器上运行此脚本可以预先测试自动安装是否能成功。
"""

import subprocess
import shutil
import platform
import os
from pathlib import Path

print("="*70)
print("Prokka_ESM3_Workflow_JLab.ipynb - 自动安装功能测试")
print("="*70)

# 1. 系统检测
print("\n[1/5] 系统检测")
print("-" * 70)
system = platform.system()
machine = platform.machine()
print(f"  操作系统: {system}")
print(f"  架构: {machine}")

# 判断是否支持
supported_systems = {
    'Linux': ['x86_64', 'aarch64'],
    'Darwin': ['x86_64', 'arm64']
}

if system in supported_systems and machine in supported_systems[system]:
    print(f"  ✅ 支持自动安装")
else:
    print(f"  ❌ 不支持自动安装")
    print(f"  支持的系统: Linux (x86_64, aarch64), macOS (x86_64, arm64)")
    exit(1)

# 2. 检查现有包管理器
print("\n[2/5] 检查现有包管理器")
print("-" * 70)

found_managers = []
for cmd in ['micromamba', 'mamba', 'conda']:
    bin_path = shutil.which(cmd)
    if bin_path:
        found_managers.append((cmd, bin_path))
        print(f"  ✅ 发现 {cmd}: {bin_path}")

if os.environ.get('CONDA_EXE'):
    if not any(name == 'conda' for name, _ in found_managers):
        found_managers.append(('conda', os.environ['CONDA_EXE']))
        print(f"  ✅ 发现 conda (CONDA_EXE): {os.environ['CONDA_EXE']}")

if found_managers:
    print(f"\n  → 检测到 {len(found_managers)} 个包管理器")
    print(f"  → Notebook 将使用已有的包管理器，无需自动安装")
else:
    print(f"  ℹ️  未检测到包管理器")
    print(f"  → Notebook 将自动安装 micromamba")

# 3. 检查安装目录权限
print("\n[3/5] 检查安装目录权限")
print("-" * 70)

install_dir = Path.home() / '.local' / 'bin'
print(f"  目标目录: {install_dir}")

try:
    install_dir.mkdir(parents=True, exist_ok=True)
    test_file = install_dir / '.test_write'
    test_file.touch()
    test_file.unlink()
    print(f"  ✅ 目录可写")
except Exception as e:
    print(f"  ❌ 目录不可写: {e}")
    exit(1)

# 4. 检查磁盘空间
print("\n[4/5] 检查磁盘空间")
print("-" * 70)

try:
    stat = os.statvfs(str(Path.home()))
    free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    print(f"  可用空间: {free_space_gb:.2f} GB")

    if free_space_gb < 1:
        print(f"  ⚠️  磁盘空间不足（建议至少 2 GB）")
    elif free_space_gb < 2:
        print(f"  ⚠️  磁盘空间较少（建议至少 2 GB）")
    else:
        print(f"  ✅ 磁盘空间充足")
except Exception as e:
    print(f"  ⚠️  无法检查磁盘空间: {e}")

# 5. 检查网络连接
print("\n[5/5] 检查网络连接")
print("-" * 70)

try:
    import urllib.request
    url = 'https://micro.mamba.pm/'
    req = urllib.request.Request(url, method='HEAD')
    response = urllib.request.urlopen(req, timeout=10)
    print(f"  ✅ 可以访问 micro.mamba.pm")
    print(f"  HTTP 状态: {response.status}")
except Exception as e:
    print(f"  ⚠️  无法访问 micro.mamba.pm: {e}")
    print(f"  → 可能需要配置代理或使用国内镜像")

# 总结
print("\n" + "="*70)
print("测试总结")
print("="*70)

if found_managers:
    print(f"\n✅ 系统已有包管理器，可以直接运行 Notebook")
    print(f"   将使用: {found_managers[0][0]}")
else:
    print(f"\n✅ 系统支持自动安装，首次运行 Notebook 将自动安装 micromamba")
    print(f"   预计需要 5-10 分钟")

print(f"\n📋 后续步骤:")
print(f"  1. 上传 Prokka_ESM3_Workflow_JLab.ipynb 到当前服务器")
print(f"  2. 在 JupyterLab 中打开 Notebook")
print(f"  3. 按顺序运行所有单元格")

if not found_managers:
    print(f"\n💡 首次运行时:")
    print(f"  - 第 2 步会自动安装 micromamba 和 Prokka")
    print(f"  - 安装位置: {install_dir}/micromamba")
    print(f"  - 环境位置: ~/micromamba/envs/prokka/")

print(f"\n" + "="*70)

