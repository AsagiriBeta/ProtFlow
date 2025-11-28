#!/usr/bin/env python3
"""
Prokka_ESM3_Workflow.ipynb 完整代码检查脚本
"""

import json
import re
from pathlib import Path

def check_notebook(notebook_path):
    """全面检查 notebook"""

    print("=" * 80)
    print("Prokka_ESM3_Workflow.ipynb 代码完整性检查")
    print("=" * 80)

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    issues = []
    warnings = []

    # 1. 基本结构检查
    print("\n[1] 基本结构检查")
    print("-" * 80)
    md_cells = [c for c in cells if c['cell_type'] == 'markdown']
    code_cells = [c for c in cells if c['cell_type'] == 'code']

    print(f"✓ 总单元格数: {len(cells)}")
    print(f"✓ Markdown 单元格: {len(md_cells)}")
    print(f"✓ 代码单元格: {len(code_cells)}")

    # 2. 章节顺序检查
    print("\n[2] 章节顺序检查")
    print("-" * 80)

    expected_sections = [
        "## 1. 环境检测与设置",
        "## 2. 安装依赖",
        "## 3. HuggingFace 认证",
        "## 4. 导入必要的库",
        "## 5. 定义工作流函数",
        "## 6. 上传输入文件",
        "## 7. 配置工作流参数",
        "## 8. 运行 Prokka 基因注释",
        "## 9. 选择要预测结构的序列",
        "## 10. 运行 ESM3 结构预测",
        "## 11. 准备 DALI 文件并创建下载包",
        "## 12. 查看结果摘要",
        "## 13. 下载结果",
        "## 14. 可选：单独查看某个 PDB 结构",
    ]

    found_sections = []
    for cell in cells:
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source'])
            for expected in expected_sections:
                if source.strip().startswith(expected):
                    found_sections.append(expected)

    for i, expected in enumerate(expected_sections, 1):
        if expected in found_sections:
            print(f"✓ {expected}")
        else:
            issues.append(f"缺失章节: {expected}")
            print(f"✗ 缺失: {expected}")

    # 3. 关键代码块检查
    print("\n[3] 关键代码块检查")
    print("-" * 80)

    all_code = '\n'.join([''.join(c['source']) for c in code_cells])

    critical_patterns = {
        "IN_COLAB 检测": r"IN_COLAB\s*=\s*['\"]google\.colab['\"]",
        "Prokka 安装": r"micromamba.*prokka",
        "HuggingFace 登录": r"from huggingface_hub import login",
        "ESM3 导入": r"from esm\.models\.esm3 import ESM3",
        "ProkkaESM3Pipeline 类": r"class ProkkaESM3Pipeline",
        "run_prokka 方法": r"def run_prokka\(",
        "load_esm3_model 方法": r"def load_esm3_model\(",
        "predict_structures 方法": r"def predict_structures\(",
        "_generate_pdb_id 方法": r"def _generate_pdb_id\(",
        "prepare_for_dali 方法": r"def prepare_for_dali\(",
        "create_download_package 方法": r"def create_download_package\(",
        "DALI 映射文件": r"pdb_id_mapping\.tsv",
        "文件上传": r"files\.upload\(\)",
        "结果下载": r"files\.download\(",
    }

    for name, pattern in critical_patterns.items():
        if re.search(pattern, all_code):
            print(f"✓ {name}")
        else:
            warnings.append(f"未找到: {name}")
            print(f"⚠ 未找到: {name}")

    # 4. 变量定义检查
    print("\n[4] 关键变量定义检查")
    print("-" * 80)

    required_vars = [
        "WORK_DIR",
        "OUTPUT_PREFIX",
        "KINGDOM",
        "NUM_STEPS",
        "MAX_SEQ_LENGTH",
        "MIN_SEQ_LENGTH",
        "pipeline",
    ]

    for var in required_vars:
        if re.search(rf'\b{var}\s*=', all_code):
            print(f"✓ {var}")
        else:
            warnings.append(f"变量未定义: {var}")
            print(f"⚠ 变量未定义: {var}")

    # 5. 导入语句检查
    print("\n[5] 必要导入检查")
    print("-" * 80)

    required_imports = {
        "sys": r"import sys",
        "os": r"import os",
        "Path": r"from pathlib import Path",
        "subprocess": r"import subprocess",
        "shutil": r"import shutil",
        "datetime": r"from datetime import datetime",
        "zipfile": r"import zipfile",
        "torch": r"import torch",
        "Bio.SeqIO": r"from Bio import SeqIO",
        "tqdm": r"from tqdm",
    }

    for name, pattern in required_imports.items():
        if re.search(pattern, all_code):
            print(f"✓ {name}")
        else:
            warnings.append(f"缺少导入: {name}")
            print(f"⚠ 缺少导入: {name}")

    # 6. DALI 功能检查
    print("\n[6] DALI 功能完整性检查")
    print("-" * 80)

    dali_checks = {
        "生成 4 字符 ID": r"string\.digits \+ string\.ascii_uppercase",
        "创建 .ent 文件": r'f"pdb{.*}\.ent"',
        "创建映射文件": r"pdb_id_mapping\.tsv",
        "写入映射内容": r"DALI_Name\\tOriginal_Name",
        "创建 pdb_list.txt": r"pdb_list\.txt",
        "创建 README": r"README\.txt",
    }

    for name, pattern in dali_checks.items():
        if re.search(pattern, all_code):
            print(f"✓ {name}")
        else:
            issues.append(f"DALI 功能缺失: {name}")
            print(f"✗ DALI 功能缺失: {name}")

    # 7. 错误处理检查
    print("\n[7] 错误处理检查")
    print("-" * 80)

    try_blocks = len(re.findall(r'\btry\s*:', all_code))
    except_blocks = len(re.findall(r'\bexcept\b', all_code))

    print(f"✓ try 块数量: {try_blocks}")
    print(f"✓ except 块数量: {except_blocks}")

    if try_blocks != except_blocks:
        warnings.append(f"try/except 数量不匹配: {try_blocks} vs {except_blocks}")
        print(f"⚠ try/except 数量不匹配")

    # 8. 代码块顺序检查
    print("\n[8] 代码执行流程检查")
    print("-" * 80)

    # 检查变量使用顺序
    critical_flow = [
        ("定义 WORK_DIR", r"WORK_DIR\s*="),
        ("创建 pipeline", r"pipeline\s*=\s*ProkkaESM3Pipeline"),
        ("运行 Prokka", r"pipeline\.run_prokka"),
        ("加载 ESM3", r"pipeline\.load_esm3_model|pipeline\.model"),
        ("预测结构", r"ESMProtein|protein\.to_pdb"),
        ("准备 DALI", r"pipeline\.prepare_for_dali"),
        ("创建压缩包", r"pipeline\.create_download_package|result_zip"),
    ]

    code_text = all_code
    last_pos = 0

    for step_name, pattern in critical_flow:
        match = re.search(pattern, code_text[last_pos:])
        if match:
            last_pos += match.start()
            print(f"✓ {step_name}")
        else:
            warnings.append(f"执行流程可能有问题: {step_name}")
            print(f"⚠ 未找到: {step_name}")

    # 9. 文件格式检查
    print("\n[9] 文件扩展名检查")
    print("-" * 80)

    file_extensions = {
        ".fna": r"\.fna",
        ".faa": r"\.faa",
        ".pdb": r"\.pdb",
        ".ent": r"\.ent",
        ".tsv": r"\.tsv",
        ".txt": r"\.txt",
        ".zip": r"\.zip",
    }

    for ext, pattern in file_extensions.items():
        if re.search(pattern, all_code):
            print(f"✓ {ext} 文件处理")
        else:
            warnings.append(f"未使用文件格式: {ext}")

    # 10. 检查章节 12 和 13 的顺序
    print("\n[10] 特殊检查: 章节 12 和 13 顺序")
    print("-" * 80)

    section_12_idx = None
    section_13_idx = None

    for i, cell in enumerate(cells):
        if cell['cell_type'] == 'markdown':
            source = ''.join(cell['source'])
            if '## 12. 查看结果摘要' in source:
                section_12_idx = i
            elif '## 13. 下载结果' in source:
                section_13_idx = i

    if section_12_idx and section_13_idx:
        if section_12_idx < section_13_idx:
            print(f"✓ 章节顺序正确: 12 (索引 {section_12_idx}) → 13 (索引 {section_13_idx})")
        else:
            issues.append("章节顺序错误: 第 13 章在第 12 章之前")
            print(f"✗ 章节顺序错误")
    else:
        warnings.append("未找到章节 12 或 13")
        print(f"⚠ 未找到章节 12 或 13")

    # 11. 检查 .ent 文件统计
    print("\n[11] DALI 文件统计检查")
    print("-" * 80)

    if re.search(r'\.glob\(["\']?\*\.ent["\']?\)', all_code):
        print(f"✓ 使用 .ent 文件统计")
    else:
        issues.append("DALI 统计应使用 .ent 而不是 .pdb")
        print(f"✗ 未使用 .ent 文件统计")

    # 总结
    print("\n" + "=" * 80)
    print("检查总结")
    print("=" * 80)

    if not issues and not warnings:
        print("\n✅ 完美！所有检查通过，代码无问题。")
        return True
    else:
        if issues:
            print(f"\n❌ 发现 {len(issues)} 个严重问题:")
            for issue in issues:
                print(f"  - {issue}")

        if warnings:
            print(f"\n⚠️  发现 {len(warnings)} 个警告:")
            for warning in warnings:
                print(f"  - {warning}")

        if not issues:
            print("\n✅ 无严重问题，只有一些警告（可忽略）")
            return True
        else:
            print("\n❌ 存在需要修复的问题")
            return False

if __name__ == "__main__":
    notebook_path = Path("Prokka_ESM3_Workflow.ipynb")

    if not notebook_path.exists():
        print(f"错误: 找不到文件 {notebook_path}")
        exit(1)

    success = check_notebook(notebook_path)
    exit(0 if success else 1)

