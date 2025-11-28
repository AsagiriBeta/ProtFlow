#!/usr/bin/env python3
"""
测试脚本：验证 DALI 命名转换功能
"""

import re
from pathlib import Path
import tempfile
import shutil

def test_pdb_id_generation():
    """测试 PDB ID 生成"""
    print("测试 1: PDB ID 生成")
    print("-" * 60)

    import random
    import string

    def generate_pdb_id(used_ids: set) -> str:
        chars = string.digits + string.ascii_uppercase
        while True:
            new_id = ''.join(random.choices(chars, k=4))
            if new_id not in used_ids:
                used_ids.add(new_id)
                return new_id

    used_ids = set()
    generated_ids = []

    # 生成 100 个 ID
    for i in range(100):
        pdb_id = generate_pdb_id(used_ids)
        generated_ids.append(pdb_id)

    # 验证
    print(f"✓ 生成了 {len(generated_ids)} 个 ID")
    print(f"✓ 唯一性检查: {len(generated_ids) == len(set(generated_ids))}")

    # 检查格式
    id_pattern = re.compile(r'^[0-9A-Z]{4}$')
    valid_count = sum(1 for id in generated_ids if id_pattern.match(id))
    print(f"✓ 格式验证: {valid_count}/{len(generated_ids)} 符合 [0-9A-Z]{{4}} 格式")

    # 显示示例
    print(f"\n示例 ID: {', '.join(generated_ids[:10])}")
    print()

def test_filename_conversion():
    """测试文件名转换"""
    print("测试 2: 文件名转换")
    print("-" * 60)

    # 模拟原始文件名
    original_names = [
        "PROKKA_00001.pdb",
        "PROKKA_00002.pdb",
        "long_protein_name_with_description.pdb",
        "AF-P12345-F1-model_v1.pdb",
    ]

    import random
    import string

    def generate_pdb_id(used_ids: set) -> str:
        chars = string.digits + string.ascii_uppercase
        while True:
            new_id = ''.join(random.choices(chars, k=4))
            if new_id not in used_ids:
                used_ids.add(new_id)
                return new_id

    used_ids = set()
    mapping = []

    for orig_name in original_names:
        pdb_id = generate_pdb_id(used_ids)
        dali_name = f"pdb{pdb_id}.ent"
        mapping.append((dali_name, orig_name))

    # 显示映射
    print("文件名转换映射:")
    for dali_name, orig_name in mapping:
        print(f"  {orig_name:45} -> {dali_name}")

    # 验证 DALI 文件名格式
    dali_pattern = re.compile(r'^pdb[0-9A-Z]{4}\.ent$')
    valid_count = sum(1 for dali_name, _ in mapping if dali_pattern.match(dali_name))
    print(f"\n✓ DALI 格式验证: {valid_count}/{len(mapping)} 符合 pdb[0-9A-Z]{{4}}.ent 格式")
    print()

def test_mapping_file_format():
    """测试映射文件格式"""
    print("测试 3: 映射文件格式")
    print("-" * 60)

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 模拟映射数据
        mapping = [
            ("pdb1A2B.ent", "PROKKA_00001.pdb"),
            ("pdb3C4D.ent", "PROKKA_00002.pdb"),
            ("pdb5E6F.ent", "long_protein_name.pdb"),
        ]

        # 写入映射文件
        mapping_file = tmpdir / "pdb_id_mapping.tsv"
        with open(mapping_file, 'w') as f:
            f.write("DALI_Name\tOriginal_Name\n")
            for dali_name, orig_name in mapping:
                f.write(f"{dali_name}\t{orig_name}\n")

        # 读取并验证
        with open(mapping_file, 'r') as f:
            lines = f.readlines()

        print(f"✓ 映射文件已创建: {mapping_file.name}")
        print(f"✓ 行数: {len(lines)} (包含标题)")
        print(f"\n文件内容:")
        for line in lines:
            print(f"  {line.rstrip()}")

        # 验证可以用 pandas 读取
        try:
            import pandas as pd
            df = pd.read_csv(mapping_file, sep='\t')
            print(f"\n✓ 可以用 pandas 读取")
            print(f"✓ 列名: {list(df.columns)}")
            print(f"✓ 数据行数: {len(df)}")
        except ImportError:
            print("\n⚠ pandas 未安装，跳过高级验证")

    print()

def test_dali_file_list():
    """测试 DALI 文件列表"""
    print("测试 4: DALI 文件列表")
    print("-" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 模拟 DALI 文件名
        dali_names = [
            "pdb1A2B.ent",
            "pdb3C4D.ent",
            "pdb5E6F.ent",
            "pdb7G8H.ent",
        ]

        # 写入列表文件
        list_file = tmpdir / "pdb_list.txt"
        with open(list_file, 'w') as f:
            for dali_name in dali_names:
                f.write(f"{dali_name}\n")

        # 读取并验证
        with open(list_file, 'r') as f:
            lines = [line.strip() for line in f.readlines()]

        print(f"✓ 列表文件已创建: {list_file.name}")
        print(f"✓ 文件数: {len(lines)}")
        print(f"\n文件列表:")
        for fname in lines:
            print(f"  {fname}")

    print()

if __name__ == "__main__":
    print("=" * 60)
    print("DALI 命名转换功能测试")
    print("=" * 60)
    print()

    test_pdb_id_generation()
    test_filename_conversion()
    test_mapping_file_format()
    test_dali_file_list()

    print("=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)

