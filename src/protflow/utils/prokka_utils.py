"""
Prokka工具函数

提供Prokka环境设置和micromamba自动安装功能。
"""

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple

try:
    from .logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def install_micromamba() -> str:
    """
    自动安装 micromamba 到用户目录
    支持 Linux 和 macOS
    
    Returns:
        micromamba二进制文件路径
    
    Raises:
        RuntimeError: 如果安装失败
    """
    print("="*60)
    print("自动安装 Micromamba")
    print("="*60)
    
    system = platform.system()
    machine = platform.machine()
    
    # 确定安装目录
    install_dir = Path.home() / '.local' / 'bin'
    install_dir.mkdir(parents=True, exist_ok=True)
    micromamba_bin = install_dir / 'micromamba'
    
    # 检查是否已经安装
    if micromamba_bin.exists():
        logger.info(f"Micromamba 已存在: {micromamba_bin}")
        if str(install_dir) not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{install_dir}:{os.environ.get('PATH', '')}"
        return str(micromamba_bin)
    
    print(f"\n检测到系统: {system} ({machine})")
    print(f"安装目录: {install_dir}")
    
    # 确定下载 URL
    if system == 'Linux':
        if machine == 'x86_64':
            url = 'https://micro.mamba.pm/api/micromamba/linux-64/latest'
        elif machine == 'aarch64':
            url = 'https://micro.mamba.pm/api/micromamba/linux-aarch64/latest'
        else:
            raise RuntimeError(f"不支持的 Linux 架构: {machine}")
    elif system == 'Darwin':  # macOS
        if machine == 'arm64':
            url = 'https://micro.mamba.pm/api/micromamba/osx-arm64/latest'
        else:
            url = 'https://micro.mamba.pm/api/micromamba/osx-64/latest'
    else:
        raise RuntimeError(f"不支持的操作系统: {system}")
    
    print(f"\n📥 正在下载 micromamba...")
    print(f"   URL: {url}")
    
    try:
        import tarfile
        import urllib.request
        
        with tempfile.NamedTemporaryFile(suffix='.tar.bz2', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            urllib.request.urlretrieve(url, tmp_path)
            print(f"✅ 下载完成: {tmp_path.stat().st_size / 1024 / 1024:.2f} MB")
            print("📦 正在解压...")
            
            with tarfile.open(tmp_path, 'r:bz2') as tar:
                for member in tar.getmembers():
                    if member.name.endswith('bin/micromamba') or member.name == 'bin/micromamba':
                        member.name = 'micromamba'
                        tar.extract(member, install_dir)
                        break
            
            tmp_path.unlink()
        
        micromamba_bin.chmod(0o755)
        print(f"✅ Micromamba 安装成功: {micromamba_bin}")
        os.environ['PATH'] = f"{install_dir}:{os.environ.get('PATH', '')}"
        
        print("\n🔧 正在初始化 micromamba...")
        try:
            subprocess.run(
                [str(micromamba_bin), 'shell', 'init', '-s', 'bash', '-p', str(Path.home() / 'micromamba')],
                capture_output=True,
                check=False
            )
            print("✅ Micromamba 初始化完成")
        except Exception as e:
            logger.warning(f"初始化警告（可忽略）: {e}")
        
        return str(micromamba_bin)
    
    except Exception as e:
        logger.error(f"安装失败: {e}")
        print("\n请手动安装 micromamba:")
        print("  Linux: curl -Ls https://micro.mamba.pm/install.sh | bash")
        print("  macOS: brew install micromamba")
        raise


def ensure_conda_with_auto_install() -> Optional[Tuple[str, str]]:
    """
    确保conda/mamba/micromamba可用，如果不存在则自动安装micromamba
    
    Returns:
        Tuple of (command_name, command_path) if found/installed, None otherwise
    """
    from .notebook_utils import check_conda_environment
    
    # 首先检查是否已存在
    conda_info = check_conda_environment()
    if conda_info:
        return conda_info
    
    # 如果不存在，尝试自动安装
    auto_install = os.environ.get('PROTFLOW_AUTO_INSTALL_MICROMAMBA', '1')
    if auto_install in ('1', 'true', 'True', 'yes', 'YES'):
        try:
            print("\n⚠️ 未检测到 conda/mamba/micromamba")
            print("\n🚀 正在自动安装 micromamba...")
            print("   (如不需要，请设置环境变量: PROTFLOW_AUTO_INSTALL_MICROMAMBA=0)")
            
            micromamba_path = install_micromamba()
            print(f"\n✅ Micromamba 安装并配置成功！")
            print(f"   路径: {micromamba_path}")
            print(f"   (已添加到当前会话的 PATH)")
            
            return ('micromamba', micromamba_path)
        
        except Exception as e:
            logger.error(f"自动安装失败: {e}")
            print("\n请选择以下任一方式手动安装:")
            print("\n方式 1 - 安装 micromamba (推荐):")
            print("  Linux: curl -Ls https://micro.mamba.pm/install.sh | bash")
            print("  macOS: brew install micromamba")
            print("\n方式 2 - 安装 conda/mamba:")
            print("  https://docs.conda.io/en/latest/miniconda.html")
            print("="*60)
            return None
    else:
        print("\n自动安装已禁用（PROTFLOW_AUTO_INSTALL_MICROMAMBA=0）")
        print("\n请选择以下任一方式手动安装:")
        print("\n方式 1 - 安装 micromamba (推荐):")
        print("  Linux: curl -Ls https://micro.mamba.pm/install.sh | bash")
        print("  macOS: brew install micromamba")
        print("\n方式 2 - 安装 conda/mamba:")
        print("  https://docs.conda.io/en/latest/miniconda.html")
        print("="*60)
        return None


def ensure_prokka_available(
    env_name: str = 'prokka',
    auto_create: bool = True,
    prokka_bin_override: Optional[str] = None
) -> List[str]:
    """
    检查并确保 Prokka 可用
    
    Args:
        env_name: conda环境名称
        auto_create: 是否自动创建环境
        prokka_bin_override: 如果设置了PROKKA_BIN环境变量，直接使用
    
    Returns:
        Prokka命令前缀列表（用于subprocess.run）
    
    Raises:
        RuntimeError: 如果Prokka不可用且无法创建
    """
    # 1. 检查环境变量 PROKKA_BIN
    if prokka_bin_override:
        prokka_path = Path(prokka_bin_override).expanduser()
        if not prokka_path.exists():
            raise FileNotFoundError(f"PROKKA_BIN 指向的文件不存在: {prokka_path}")
        logger.info(f"使用 PROKKA_BIN: {prokka_path}")
        return [str(prokka_path)]
    
    override = os.environ.get('PROKKA_BIN')
    if override:
        prokka_path = Path(override).expanduser()
        if not prokka_path.exists():
            raise FileNotFoundError(f"PROKKA_BIN 指向的文件不存在: {prokka_path}")
        logger.info(f"使用 PROKKA_BIN: {prokka_path}")
        return [str(prokka_path)]
    
    # 2. 检查是否有 conda/mamba 环境
    conda_info = ensure_conda_with_auto_install()
    
    if not conda_info:
        raise RuntimeError(
            "未找到可用的 Prokka 安装。\n"
            "请安装 conda/mamba/micromamba 或设置 PROKKA_BIN 环境变量"
        )
    
    conda_cmd, conda_path = conda_info
    
    # 检查环境是否存在
    try:
        env_list = subprocess.run(
            [conda_path, 'env', 'list'],
            capture_output=True,
            text=True,
            check=True
        )
        env_exists = env_name in env_list.stdout
    except Exception:
        env_exists = False
    
    # 构建 prokka 命令
    if conda_cmd == 'conda':
        prokka_cmd = ['conda', 'run', '-n', env_name, 'prokka']
    else:
        prokka_cmd = [conda_path, 'run', '-n', env_name, 'prokka']
    
    # 如果环境不存在，尝试创建
    if not env_exists:
        if not auto_create:
            raise RuntimeError(
                f"未检测到 {conda_cmd} 环境 '{env_name}'，并且自动创建被禁用。\n"
                f"请手动创建: {conda_cmd} create -n {env_name} -c conda-forge -c bioconda prokka"
            )
        
        print(f"📦 正在使用 {conda_cmd} 创建环境: {env_name}")
        print("   这可能需要 5-10 分钟...\n")
        
        try:
            create_cmd = [
                conda_path, 'create', '-y', '-n', env_name,
                '-c', 'conda-forge', '-c', 'bioconda', '-c', 'defaults',
                'prokka'
            ]
            subprocess.run(create_cmd, check=True)
            print('✅ Prokka 环境创建成功！')
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"创建 Prokka 环境失败。\n"
                f"请手动安装: {conda_cmd} create -n {env_name} -c conda-forge -c bioconda prokka"
            ) from e
    else:
        print(f"✅ 环境 '{env_name}' 已存在")
    
    # 验证 Prokka 可用性
    try:
        version_cmd = prokka_cmd + ['--version']
        result = subprocess.run(version_cmd, capture_output=True, text=True, check=True)
        logger.info(f"Prokka 可用: {result.stdout.strip()}")
        return prokka_cmd
    except subprocess.CalledProcessError as e:
        logger.error(f"Prokka 验证失败: {e}")
        raise
