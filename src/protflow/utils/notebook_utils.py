"""
Utility functions for Jupyter notebooks in ProtFlow.

This module provides common functions used across notebooks including:
- Dependency checking and installation
- Environment setup
- Common imports and configurations
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union


def check_and_install_packages(
    packages: List[Union[str, Tuple[str, str]]],
    quiet: bool = False
) -> None:
    """
    Check if Python packages are installed and install missing ones.
    
    Args:
        packages: List of package names or tuples of (import_name, package_name)
                 For example: ['numpy', ('cv2', 'opencv-python')]
        quiet: If True, suppress output messages
        
    Example:
        >>> check_and_install_packages(['numpy', 'pandas', ('cv2', 'opencv-python')])
    """
    missing_packages = []
    
    for pkg in packages:
        # Handle tuples of (import_name, package_name)
        if isinstance(pkg, tuple):
            import_name, package_name = pkg
        else:
            import_name = package_name = pkg
            
        try:
            __import__(import_name)
            if not quiet:
                print(f"✓ {package_name} 已安装")
        except ImportError:
            missing_packages.append((import_name, package_name))
            if not quiet:
                print(f"⚠ {package_name} 未安装")
    
    # Install missing packages
    if missing_packages:
        if not quiet:
            print(f"\n正在安装 {len(missing_packages)} 个缺失的包...")
        
        for import_name, package_name in missing_packages:
            if not quiet:
                print(f"  安装 {package_name}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name],
                    stdout=subprocess.DEVNULL if quiet else None,
                    stderr=subprocess.DEVNULL if quiet else None
                )
                if not quiet:
                    print(f"  ✓ {package_name} 安装完成")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ {package_name} 安装失败: {e}")
                raise
        
        if not quiet:
            print(f"\n✓ 所有依赖安装完成")
    elif not quiet:
        print("\n✓ 所有依赖已安装")


def setup_notebook_environment(
    project_root: Optional[Path] = None,
    work_dir_name: str = 'notebook_runs',
    add_to_path: bool = True
) -> Dict[str, Path]:
    """
    Setup common notebook environment variables and paths.
    
    Args:
        project_root: Project root directory. If None, auto-detect from PROTFLOW_ROOT
                     environment variable or current working directory.
        work_dir_name: Name of the working directory to create
        add_to_path: Whether to add project src directory to Python path
        
    Returns:
        Dictionary containing:
            - 'PROJECT_ROOT': Project root directory
            - 'WORK_DIR': Working directory for outputs
            - 'SRC_DIR': Source code directory
            - 'DATA_DIR': Data directory
            
    Example:
        >>> paths = setup_notebook_environment(work_dir_name='structure_runs')
        >>> print(f"Working directory: {paths['WORK_DIR']}")
    """
    # Determine project root
    if project_root is None:
        project_root = Path(os.environ.get('PROTFLOW_ROOT', Path.cwd())).resolve()
    else:
        project_root = Path(project_root).resolve()
    
    # Setup directories
    src_dir = project_root / 'src'
    work_dir = project_root / work_dir_name
    data_dir = project_root / 'data'
    
    # Create working directory
    work_dir.mkdir(exist_ok=True, parents=True)
    
    # Add src to path if requested
    if add_to_path and src_dir.exists():
        src_str = str(src_dir)
        if src_str not in sys.path:
            sys.path.insert(0, src_str)
    
    paths = {
        'PROJECT_ROOT': project_root,
        'WORK_DIR': work_dir,
        'SRC_DIR': src_dir,
        'DATA_DIR': data_dir,
    }
    
    return paths


def print_environment_info(paths: Dict[str, Path], verbose: bool = True) -> None:
    """
    Print environment information for debugging.
    
    Args:
        paths: Dictionary of paths from setup_notebook_environment()
        verbose: If True, print detailed information
    """
    # Detect environment
    in_colab = 'google.colab' in sys.modules
    in_jupyterhub = bool(os.environ.get('JUPYTERHUB_SERVICE_PREFIX'))
    
    print("=" * 60)
    print("环境信息")
    print("=" * 60)
    
    if in_colab:
        print("✓ 运行环境: Google Colab")
    elif in_jupyterhub:
        print("✓ 运行环境: JupyterHub/JupyterLab 服务器")
    else:
        print("✓ 运行环境: 本地环境")
    
    print(f"\n项目根目录: {paths['PROJECT_ROOT']}")
    print(f"工作目录: {paths['WORK_DIR']}")
    
    if verbose:
        print(f"源代码目录: {paths['SRC_DIR']}")
        print(f"数据目录: {paths['DATA_DIR']}")
        print(f"\nPython 版本: {sys.version.split()[0]}")
        print(f"Python 路径: {sys.executable}")
    
    print("=" * 60)


def check_conda_environment() -> Optional[Tuple[str, str]]:
    """
    Check if conda/mamba/micromamba is available.
    
    Returns:
        Tuple of (command_name, command_path) if found, None otherwise
        
    Example:
        >>> conda = check_conda_environment()
        >>> if conda:
        ...     cmd_name, cmd_path = conda
        ...     print(f"Found {cmd_name} at {cmd_path}")
    """
    # Check for micromamba and mamba first (faster)
    for cmd in ['micromamba', 'mamba']:
        bin_path = shutil.which(cmd)
        if bin_path:
            return (cmd, bin_path)
    
    # Check for conda
    conda_exe = os.environ.get('CONDA_EXE') or shutil.which('conda')
    if conda_exe:
        return ('conda', conda_exe)
    
    return None


def ensure_conda_env(
    env_name: str,
    packages: List[str],
    channels: Optional[List[str]] = None,
    auto_create: bool = True
) -> List[str]:
    """
    Ensure a conda environment exists with specified packages.
    
    Args:
        env_name: Name of the conda environment
        packages: List of packages to install in the environment
        channels: List of conda channels to use (default: ['conda-forge', 'bioconda'])
        auto_create: Whether to automatically create the environment if it doesn't exist
        
    Returns:
        Command prefix to run commands in the environment
        
    Raises:
        RuntimeError: If conda is not available or environment creation fails
        
    Example:
        >>> cmd = ensure_conda_env('myenv', ['package1', 'package2'])
        >>> # Use cmd as: subprocess.run(cmd + ['my-tool', '--version'])
    """
    conda_info = check_conda_environment()
    
    if conda_info is None:
        raise RuntimeError(
            "未找到 conda/mamba/micromamba。\n"
            "请安装其中之一：\n"
            "  - micromamba: https://mamba.readthedocs.io/en/latest/installation.html\n"
            "  - conda: https://docs.conda.io/en/latest/miniconda.html"
        )
    
    conda_cmd, conda_path = conda_info
    
    if channels is None:
        channels = ['conda-forge', 'bioconda', 'defaults']
    
    # Check if environment exists
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
    
    # Build run command
    if conda_cmd == 'conda':
        run_cmd = ['conda', 'run', '-n', env_name]
    else:
        run_cmd = [conda_path, 'run', '-n', env_name]
    
    # Create environment if needed
    if not env_exists:
        if not auto_create:
            raise RuntimeError(
                f"环境 '{env_name}' 不存在，且自动创建被禁用。\n"
                f"请手动创建: {conda_cmd} create -n {env_name} -c conda-forge -c bioconda {' '.join(packages)}"
            )
        
        print(f"📦 正在创建 {conda_cmd} 环境: {env_name}")
        print("   这可能需要几分钟...\n")
        
        create_cmd = [conda_path, 'create', '-y', '-n', env_name]
        for channel in channels:
            create_cmd.extend(['-c', channel])
        create_cmd.extend(packages)
        
        try:
            subprocess.run(create_cmd, check=True)
            print(f'✓ 环境 {env_name} 创建成功！')
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"创建环境失败。\n"
                f"请手动安装: {conda_cmd} create -n {env_name} -c conda-forge -c bioconda {' '.join(packages)}"
            ) from e
    else:
        print(f"✓ 环境 '{env_name}' 已存在")
    
    return run_cmd


def load_protflow_config(config_path: Optional[Path] = None) -> 'ProtFlowConfig':
    """
    Load ProtFlow configuration.
    
    Args:
        config_path: Path to config file. If None, use default configuration.
        
    Returns:
        ProtFlowConfig instance
        
    Example:
        >>> from protflow.utils.notebook_utils import load_protflow_config
        >>> config = load_protflow_config()
        >>> print(config.base_dir)  # Access configuration attributes
        >>> print(config.esm3_model)  # ESM3 model name
    """
    from protflow.utils.config import ProtFlowConfig
    
    if config_path and Path(config_path).exists():
        return ProtFlowConfig.from_file(config_path)
    else:
        return ProtFlowConfig()


# Common package groups for different notebook types
CORE_PACKAGES = [
    'biopython',
    'pandas',
    'numpy',
    'tqdm',
]

ESM3_PACKAGES = CORE_PACKAGES + [
    ('esm', 'esm>=3.2.1.post1'),
    'huggingface_hub',
    ('torch', 'torch>=2.9.0'),
]

VISUALIZATION_PACKAGES = [
    'matplotlib',
    ('py3Dmol', 'py3Dmol>=2.5.3'),
]

NOTEBOOK_PACKAGES = [
    'ipykernel',
]


def setup_esm3_notebook(work_dir_name: str = 'esm3_runs') -> Dict[str, Path]:
    """
    Setup environment for ESM3-based notebooks.
    
    This is a convenience function that:
    1. Checks and installs ESM3 dependencies
    2. Sets up the notebook environment
    3. Prints environment info
    
    Args:
        work_dir_name: Name of the working directory
        
    Returns:
        Dictionary of paths from setup_notebook_environment()
    """
    print("正在检查 ESM3 依赖...")
    check_and_install_packages(ESM3_PACKAGES)
    
    paths = setup_notebook_environment(work_dir_name=work_dir_name)
    print_environment_info(paths, verbose=False)
    
    return paths


def setup_analysis_notebook(work_dir_name: str = 'analysis_runs') -> Dict[str, Path]:
    """
    Setup environment for analysis notebooks.
    
    This is a convenience function that:
    1. Checks and installs core and visualization dependencies
    2. Sets up the notebook environment
    3. Prints environment info
    
    Args:
        work_dir_name: Name of the working directory
        
    Returns:
        Dictionary of paths from setup_notebook_environment()
    """
    print("正在检查依赖...")
    check_and_install_packages(CORE_PACKAGES + VISUALIZATION_PACKAGES)
    
    paths = setup_notebook_environment(work_dir_name=work_dir_name)
    print_environment_info(paths, verbose=False)
    
    return paths
