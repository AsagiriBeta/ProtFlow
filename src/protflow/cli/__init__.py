"""
ProtFlow命令行工具模块

提供各种命令行工具和脚本：
- runner: 主运行脚本
- check_deps: 依赖检查
- validate_notebook: Notebook验证
- tm_align_comparison: TM-align结构比对工具
"""
from .runner import main as run_pipeline
from .check_deps import main as check_dependencies
from .validate_notebook import main as validate_notebook

__all__ = [
    'run_pipeline',
    'check_dependencies',
    'validate_notebook',
]
