#!/usr/bin/env python3
"""
额外的代码质量和逻辑检查
"""

import json
import re
from pathlib import Path

def additional_checks(notebook_path):
    """额外的深度检查"""

    print("=" * 80)
    print("深度代码质量检查")
    print("=" * 80)

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
    all_code = '\n'.join([''.join(c['source']) for c in code_cells])

    issues = []

    # 1. 检查配置参数的合理性
    print("\n[1] 配置参数合理性检查")
    print("-" * 80)

    param_checks = [
        (r'NUM_STEPS\s*=\s*(\d+)', 'NUM_STEPS', lambda x: 1 <= int(x) <= 100),
        (r'MAX_SEQ_LENGTH\s*=\s*(\d+)', 'MAX_SEQ_LENGTH', lambda x: 10 <= int(x) <= 10000),
        (r'MIN_SEQ_LENGTH\s*=\s*(\d+)', 'MIN_SEQ_LENGTH', lambda x: 1 <= int(x) <= 1000),
        (r'CPUS\s*=\s*(\d+)', 'CPUS', lambda x: 1 <= int(x) <= 128),
    ]

    for pattern, name, validator in param_checks:
        match = re.search(pattern, all_code)
        if match:
            value = match.group(1)
            if validator(value):
                print(f"✓ {name} = {value} (合理)")
            else:
                issues.append(f"{name} = {value} 值不合理")
                print(f"⚠ {name} = {value} (可能不合理)")
        else:
            print(f"⚠ 未找到 {name}")

    # 2. 检查文件路径处理
    print("\n[2] 文件路径处理检查")
    print("-" * 80)

    path_patterns = [
        (r'Path\(["\']', "使用 Path 对象"),
        (r'\.exists\(\)', "检查文件存在"),
        (r'\.mkdir\(', "创建目录"),
        (r'\.glob\(', "文件遍历"),
    ]

    for pattern, desc in path_patterns:
        if re.search(pattern, all_code):
            print(f"✓ {desc}")
        else:
            print(f"⚠ 未使用: {desc}")

    # 3. 检查资源清理
    print("\n[3] 资源管理检查")
    print("-" * 80)

    with_statements = len(re.findall(r'\bwith\s+open\(', all_code))
    print(f"✓ with open() 使用次数: {with_statements}")

    if with_statements > 0:
        print(f"✓ 正确使用上下文管理器")

    # 4. 检查用户友好性
    print("\n[4] 用户友好性检查")
    print("-" * 80)

    user_friendly = [
        (r'print\(["\'].*✓', "成功提示"),
        (r'print\(["\'].*⚠', "警告提示"),
        (r'print\(["\'].*❌', "错误提示"),
        (r'tqdm\(', "进度条"),
        (r'=\*60', "分隔线"),
    ]

    for pattern, desc in user_friendly:
        count = len(re.findall(pattern, all_code))
        if count > 0:
            print(f"✓ {desc}: {count} 处")
        else:
            print(f"⚠ 未使用: {desc}")

    # 5. 检查注释完整性
    print("\n[5] 代码注释检查")
    print("-" * 80)

    comment_lines = len(re.findall(r'^\s*#[^#%]', all_code, re.MULTILINE))
    docstrings = len(re.findall(r'"""[\s\S]*?"""', all_code))
    total_lines = len(all_code.split('\n'))

    print(f"✓ 单行注释: {comment_lines} 行")
    print(f"✓ 文档字符串: {docstrings} 个")
    print(f"✓ 总代码行数: {total_lines}")

    if total_lines > 0:
        comment_ratio = (comment_lines / total_lines) * 100
        print(f"✓ 注释比例: {comment_ratio:.1f}%")

    # 6. 检查 DALI 特定逻辑
    print("\n[6] DALI 功能逻辑检查")
    print("-" * 80)

    # 检查是否正确使用 used_ids 防止重复
    if re.search(r'used_ids\s*=\s*set\(\)', all_code):
        print(f"✓ 使用 set() 防止 ID 重复")
    else:
        issues.append("未找到 used_ids 集合")
        print(f"✗ 未找到 ID 去重逻辑")

    # 检查是否生成 4 字符 ID
    if re.search(r'random\.choices\(.*k\s*=\s*4', all_code):
        print(f"✓ 生成 4 字符随机 ID")
    else:
        issues.append("ID 生成逻辑可能有误")
        print(f"⚠ ID 长度可能不正确")

    # 检查是否复制文件而不是移动
    if re.search(r'shutil\.copy2?\(', all_code):
        print(f"✓ 使用复制而非移动（保留原文件）")
    else:
        print(f"⚠ 未使用 shutil.copy")

    # 检查映射文件是否包含标题行
    if re.search(r'DALI_Name\\tOriginal_Name', all_code):
        print(f"✓ 映射文件包含标题行")
    else:
        issues.append("映射文件缺少标题")
        print(f"✗ 映射文件缺少标题")

    # 7. 检查变量命名规范
    print("\n[7] 变量命名规范检查")
    print("-" * 80)

    # 全大写常量
    constants = re.findall(r'\b([A-Z_]{2,})\s*=', all_code)
    constants = set(constants) - {'IN_COLAB'}  # 排除已知的
    print(f"✓ 发现常量: {len(constants)} 个")

    # 类名（大写开头）
    classes = re.findall(r'class\s+([A-Z][a-zA-Z0-9]*)', all_code)
    print(f"✓ 发现类: {', '.join(classes)}")

    # 方法名（小写+下划线）
    methods = re.findall(r'def\s+([a-z_][a-z0-9_]*)\(', all_code)
    print(f"✓ 发现方法: {len(set(methods))} 个")

    # 8. 检查异常处理的完整性
    print("\n[8] 异常处理完整性检查")
    print("-" * 80)

    try_blocks = list(re.finditer(r'try\s*:', all_code))

    for i, match in enumerate(try_blocks, 1):
        # 检查后续是否有 except
        code_after = all_code[match.end():match.end()+500]
        if 'except' in code_after:
            # 检查是否有错误信息输出
            if 'print' in code_after or 'traceback' in code_after:
                print(f"✓ try 块 #{i}: 有完整的错误处理")
            else:
                print(f"⚠ try 块 #{i}: 可能缺少错误信息输出")
        else:
            issues.append(f"try 块 #{i} 缺少 except")
            print(f"✗ try 块 #{i}: 缺少 except")

    # 9. 检查 Colab 兼容性
    print("\n[9] Google Colab 兼容性检查")
    print("-" * 80)

    colab_checks = [
        (r'IN_COLAB.*google\.colab', "Colab 环境检测"),
        (r'if IN_COLAB:', "Colab 条件分支"),
        (r'files\.upload\(\)', "Colab 文件上传"),
        (r'files\.download\(', "Colab 文件下载"),
        (r'!.*micromamba', "Shell 命令执行"),
    ]

    for pattern, desc in colab_checks:
        if re.search(pattern, all_code):
            print(f"✓ {desc}")
        else:
            print(f"⚠ 未找到: {desc}")

    # 10. 检查 GPU 支持
    print("\n[10] GPU 支持检查")
    print("-" * 80)

    gpu_checks = [
        (r'torch\.cuda\.is_available\(\)', "GPU 可用性检测"),
        (r'\.to\(.*device', "模型转移到设备"),
        (r'device\s*=.*cuda', "CUDA 设备选择"),
    ]

    for pattern, desc in gpu_checks:
        if re.search(pattern, all_code):
            print(f"✓ {desc}")
        else:
            print(f"⚠ 未找到: {desc}")

    # 总结
    print("\n" + "=" * 80)
    print("深度检查总结")
    print("=" * 80)

    if not issues:
        print("\n✅ 所有深度检查通过！代码质量优秀。")
        return True
    else:
        print(f"\n⚠️  发现 {len(issues)} 个潜在问题:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n建议修复以上问题以提高代码质量。")
        return False

if __name__ == "__main__":
    notebook_path = Path("Prokka_ESM3_Workflow.ipynb")

    if not notebook_path.exists():
        print(f"错误: 找不到文件 {notebook_path}")
        exit(1)

    success = additional_checks(notebook_path)
    exit(0 if success else 1)

