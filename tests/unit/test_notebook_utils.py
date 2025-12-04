"""Tests for notebook utility functions."""

import sys
import shutil
import tempfile
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from protflow.utils import notebook_utils


def test_setup_notebook_environment():
    """Test notebook environment setup."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Setup environment
        paths = notebook_utils.setup_notebook_environment(
            project_root=project_root,
            work_dir_name='test_runs',
            add_to_path=False
        )
        
        # Check paths exist
        assert paths['PROJECT_ROOT'] == project_root
        assert paths['WORK_DIR'].exists()
        assert paths['WORK_DIR'].name == 'test_runs'
        assert 'SRC_DIR' in paths
        assert 'DATA_DIR' in paths


def test_check_conda_environment():
    """Test conda environment detection."""
    # This will return None or a tuple depending on system
    result = notebook_utils.check_conda_environment()
    
    if result is not None:
        assert isinstance(result, tuple)
        assert len(result) == 2
        cmd_name, cmd_path = result
        assert cmd_name in ['conda', 'mamba', 'micromamba']
        assert Path(cmd_path).exists()


def test_package_groups():
    """Test that package groups are defined."""
    assert isinstance(notebook_utils.CORE_PACKAGES, list)
    assert len(notebook_utils.CORE_PACKAGES) > 0
    
    assert isinstance(notebook_utils.ESM3_PACKAGES, list)
    assert len(notebook_utils.ESM3_PACKAGES) > len(notebook_utils.CORE_PACKAGES)
    
    assert isinstance(notebook_utils.VISUALIZATION_PACKAGES, list)
    assert isinstance(notebook_utils.NOTEBOOK_PACKAGES, list)


def test_print_environment_info(capsys):
    """Test environment info printing."""
    paths = {
        'PROJECT_ROOT': Path('/tmp/test'),
        'WORK_DIR': Path('/tmp/test/runs'),
        'SRC_DIR': Path('/tmp/test/src'),
        'DATA_DIR': Path('/tmp/test/data'),
    }
    
    notebook_utils.print_environment_info(paths, verbose=True)
    
    captured = capsys.readouterr()
    assert '环境信息' in captured.out
    assert 'PROJECT_ROOT' in captured.out or '项目根目录' in captured.out
