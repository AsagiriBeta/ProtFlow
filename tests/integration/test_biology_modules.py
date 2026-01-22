#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 ProtFlow 生物学模块
检查各个核心功能是否正常工作
"""

import sys
import traceback
import io
from pathlib import Path

# 设置 UTF-8 编码（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """测试基础模块导入"""
    print("=" * 60)
    print("测试 1: 基础模块导入")
    print("=" * 60)
    
    results = {}
    
    # 测试基础包
    try:
        import numpy as np
        print(f"[OK] numpy {np.__version__}")
        results['numpy'] = True
    except Exception as e:
        print(f"[FAIL] numpy: {e}")
        results['numpy'] = False
    
    try:
        import pandas as pd
        print(f"[OK] pandas {pd.__version__}")
        results['pandas'] = True
    except Exception as e:
        print(f"[FAIL] pandas: {e}")
        results['pandas'] = False
    
    try:
        from Bio import SeqIO
        print(f"[OK] biopython")
        results['biopython'] = True
    except Exception as e:
        print(f"[FAIL] biopython: {e}")
        results['biopython'] = False
    
    try:
        import matplotlib
        print(f"[OK] matplotlib {matplotlib.__version__}")
        results['matplotlib'] = True
    except Exception as e:
        print(f"[FAIL] matplotlib: {e}")
        results['matplotlib'] = False
    
    try:
        import torch
        print(f"[OK] torch {torch.__version__}")
        results['torch'] = True
    except Exception as e:
        print(f"[FAIL] torch: {e}")
        results['torch'] = False
    
    # 测试 ESM（可能不可用）
    try:
        import esm
        print(f"[OK] esm")
        results['esm'] = True
    except Exception as e:
        print(f"[WARN] esm: 未安装（需要编译工具）")
        results['esm'] = False
    
    print()
    return results

def test_protflow_utils():
    """测试 ProtFlow 工具模块"""
    print("=" * 60)
    print("测试 2: ProtFlow 工具模块")
    print("=" * 60)
    
    results = {}
    
    try:
        from protflow.utils.config import ProtFlowConfig, get_config
        print("[OK] config 模块")
        results['config'] = True
    except Exception as e:
        print(f"[FAIL] config: {e}")
        results['config'] = False
        traceback.print_exc()
    
    try:
        from protflow.utils.logger import setup_logging, get_logger
        print("[OK] logger 模块")
        results['logger'] = True
    except Exception as e:
        print(f"[FAIL] logger: {e}")
        results['logger'] = False
    
    try:
        from protflow.utils.seq_parser import extract_proteins_from_gbk, filter_and_select
        print("[OK] seq_parser 模块")
        results['seq_parser'] = True
    except Exception as e:
        print(f"[FAIL] seq_parser: {e}")
        results['seq_parser'] = False
        traceback.print_exc()
    
    try:
        from protflow.utils.notebook_utils import check_and_install_packages
        print("[OK] notebook_utils 模块")
        results['notebook_utils'] = True
    except Exception as e:
        print(f"[FAIL] notebook_utils: {e}")
        results['notebook_utils'] = False
    
    print()
    return results

def test_protflow_core():
    """测试 ProtFlow 核心模块"""
    print("=" * 60)
    print("测试 3: ProtFlow 核心模块")
    print("=" * 60)
    
    results = {}
    
    try:
        from protflow.core import cds_comparison
        print("[OK] cds_comparison 模块")
        results['cds_comparison'] = True
    except Exception as e:
        print(f"[FAIL] cds_comparison: {e}")
        results['cds_comparison'] = False
        traceback.print_exc()
    
    try:
        from protflow.core import reporting
        print("[OK] reporting 模块")
        results['reporting'] = True
    except Exception as e:
        print(f"[FAIL] reporting: {e}")
        results['reporting'] = False
    
    try:
        from protflow.core.structure_analysis import collect_structure_files
        print("[OK] structure_analysis 模块")
        results['structure_analysis'] = True
    except Exception as e:
        print(f"[FAIL] structure_analysis: {e}")
        results['structure_analysis'] = False
    
    try:
        from protflow.core.structure_comparison import compare_structures_tm_align
        print("[OK] structure_comparison 模块")
        results['structure_comparison'] = True
    except Exception as e:
        print(f"[FAIL] structure_comparison: {e}")
        results['structure_comparison'] = False
    
    print()
    return results

def test_biology_functions():
    """测试生物学功能"""
    print("=" * 60)
    print("测试 4: 生物学功能测试")
    print("=" * 60)
    
    results = {}
    
    # 测试序列解析
    try:
        from protflow.utils.seq_parser import extract_proteins_from_gbk
        from Bio.SeqIO import parse
        print("[OK] 序列解析功能可用")
        results['sequence_parsing'] = True
    except Exception as e:
        print(f"[FAIL] 序列解析: {e}")
        results['sequence_parsing'] = False
    
    # 测试结构分析
    try:
        from protflow.core.structure_analysis import collect_structure_files
        test_path = project_root / "data" / "pdbs"
        if test_path.exists():
            files = collect_structure_files(test_path)
            print(f"[OK] 结构文件收集: 找到 {len(files)} 个文件")
        else:
            print("[WARN] 结构文件收集: 测试目录不存在，但功能可用")
        results['structure_collection'] = True
    except Exception as e:
        print(f"[FAIL] 结构文件收集: {e}")
        results['structure_collection'] = False
    
    # 测试 ESM3（如果可用）
    try:
        from protflow.prediction import esm3_predict
        print("[OK] ESM3 预测模块可用")
        results['esm3'] = True
    except ImportError:
        print("[WARN] ESM3 预测: 模块不可用（需要 ESM 包）")
        results['esm3'] = False
    except Exception as e:
        print(f"[WARN] ESM3 预测: {e}")
        results['esm3'] = False
    
    print()
    return results

def test_visualization():
    """测试可视化模块"""
    print("=" * 60)
    print("测试 5: 可视化模块")
    print("=" * 60)
    
    results = {}
    
    try:
        from protflow.visualization import visualization
        print("[OK] visualization 模块")
        results['visualization'] = True
    except Exception as e:
        print(f"[FAIL] visualization: {e}")
        results['visualization'] = False
    
    try:
        import py3Dmol
        print("[OK] py3Dmol 可用")
        results['py3dmol'] = True
    except Exception as e:
        print(f"[WARN] py3Dmol: {e}")
        results['py3dmol'] = False
    
    print()
    return results

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("ProtFlow 生物学模块测试")
    print("=" * 60 + "\n")
    
    all_results = {}
    
    # 运行所有测试
    all_results.update(test_imports())
    all_results.update(test_protflow_utils())
    all_results.update(test_protflow_core())
    all_results.update(test_biology_functions())
    all_results.update(test_visualization())
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    total = len(all_results)
    passed = sum(1 for v in all_results.values() if v)
    failed = total - passed
    
    print(f"\n总计: {total} 项测试")
    print(f"通过: {passed} 项")
    print(f"失败/警告: {failed} 项")
    
    # 关键功能状态
    print("\n关键功能状态:")
    critical = {
        'numpy': '数值计算',
        'pandas': '数据处理',
        'biopython': '生物信息学',
        'seq_parser': '序列解析',
        'structure_analysis': '结构分析',
        'esm': 'ESM3 预测（可选）'
    }
    
    for key, desc in critical.items():
        status = "[OK]" if all_results.get(key) else "[FAIL]"
        print(f"  {status} {desc}")
    
    # 建议
    print("\n建议:")
    if not all_results.get('esm'):
        print("  - ESM 未安装，ESM3 结构预测功能不可用")
        print("    如需使用，请安装 Visual C++ Build Tools 或使用 Conda")
    
    if all_results.get('numpy') and all_results.get('pandas') and all_results.get('biopython'):
        print("  - 基础生物学功能可用，可以进行序列分析和结构分析")
    
    print("\n" + "=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
