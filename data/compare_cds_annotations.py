#!/usr/bin/env python3
"""
比较 antiSMASH 和 Prokka 输出的 CDS 注释

该脚本可以：
1. 从 antiSMASH 和 Prokka 的 GenBank 输出中提取 CDS 特征
2. 比较两者的 CDS 数量、位置和注释信息
3. 生成详细的比较报告

用法:
    python compare_cds_annotations.py --antismash <antismash.gbk> --prokka <prokka.gbk>
    python compare_cds_annotations.py --antismash-dir <dir> --prokka-dir <dir>
"""

from pathlib import Path
from typing import List, Dict, Tuple
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature
import argparse
import sys
from collections import defaultdict
import pandas as pd


class CDSAnnotation:
    """表示一个 CDS 注释"""

    def __init__(self, feature: SeqFeature, record_id: str, source: str):
        self.feature = feature
        self.record_id = record_id
        self.source = source  # 'antismash' or 'prokka'

        # 提取关键信息
        self.start = int(feature.location.start)
        self.end = int(feature.location.end)
        self.strand = feature.location.strand
        self.length = self.end - self.start

        # 提取 qualifiers
        q = feature.qualifiers
        self.gene = q.get('gene', [''])[0]
        self.locus_tag = q.get('locus_tag', [''])[0]
        self.product = q.get('product', [''])[0]
        self.protein_id = q.get('protein_id', [''])[0]
        self.translation = q.get('translation', [''])[0]

    def __repr__(self):
        return f"CDS({self.record_id}:{self.start}-{self.end}, {self.gene or self.locus_tag})"

    def location_key(self) -> Tuple[int, int, int]:
        """返回用于位置比较的键 (start, end, strand)"""
        return (self.start, self.end, self.strand or 0)

    def overlaps_with(self, other: 'CDSAnnotation', tolerance: int = 10) -> bool:
        """检查是否与另一个 CDS 重叠（允许一定容差）"""
        if self.strand != other.strand:
            return False

        # 检查位置重叠
        start_diff = abs(self.start - other.start)
        end_diff = abs(self.end - other.end)

        return start_diff <= tolerance and end_diff <= tolerance

    def to_dict(self) -> Dict:
        """转换为字典格式用于报告"""
        return {
            'record_id': self.record_id,
            'source': self.source,
            'start': self.start,
            'end': self.end,
            'strand': '+' if self.strand == 1 else ('-' if self.strand == -1 else '.'),
            'length': self.length,
            'gene': self.gene,
            'locus_tag': self.locus_tag,
            'product': self.product,
            'protein_id': self.protein_id,
            'has_translation': bool(self.translation),
            'translation_length': len(self.translation) if self.translation else 0
        }


def extract_cds_from_gbk(gbk_path: Path, source: str) -> List[CDSAnnotation]:
    """从 GenBank 文件中提取所有 CDS 特征"""
    cds_list = []

    try:
        for record in SeqIO.parse(str(gbk_path), 'genbank'):
            for feature in record.features:
                if feature.type == 'CDS':
                    cds = CDSAnnotation(feature, record.id, source)
                    cds_list.append(cds)
    except Exception as e:
        print(f"错误：无法解析 {gbk_path}: {e}", file=sys.stderr)
        return []

    return cds_list


def extract_cds_from_directory(directory: Path, source: str) -> List[CDSAnnotation]:
    """从目录中的所有 GenBank 文件提取 CDS"""
    all_cds = []

    # 查找所有 .gbk 和 .gbff 文件
    gbk_files = list(directory.glob('**/*.gbk')) + list(directory.glob('**/*.gbff'))

    if not gbk_files:
        print(f"警告：在 {directory} 中未找到 GenBank 文件", file=sys.stderr)
        return []

    print(f"从 {directory} 找到 {len(gbk_files)} 个 GenBank 文件")

    for gbk_file in gbk_files:
        cds_list = extract_cds_from_gbk(gbk_file, source)
        all_cds.extend(cds_list)
        print(f"  {gbk_file.name}: {len(cds_list)} 个 CDS")

    return all_cds


def compare_cds_lists(antismash_cds: List[CDSAnnotation],
                     prokka_cds: List[CDSAnnotation],
                     tolerance: int = 10) -> Dict:
    """比较两个 CDS 列表"""

    print(f"\n{'='*60}")
    print(f"CDS 注释比较报告")
    print(f"{'='*60}\n")

    # 基本统计
    print(f"antiSMASH CDS 数量: {len(antismash_cds)}")
    print(f"Prokka CDS 数量: {len(prokka_cds)}")
    print(f"差异: {abs(len(antismash_cds) - len(prokka_cds))}")

    # 按记录ID分组
    antismash_by_record = defaultdict(list)
    prokka_by_record = defaultdict(list)

    for cds in antismash_cds:
        antismash_by_record[cds.record_id].append(cds)

    for cds in prokka_cds:
        prokka_by_record[cds.record_id].append(cds)

    # 记录所有的记录ID
    all_records = set(antismash_by_record.keys()) | set(prokka_by_record.keys())

    # 比较结果
    results = {
        'total_antismash': len(antismash_cds),
        'total_prokka': len(prokka_cds),
        'matched': [],
        'antismash_only': [],
        'prokka_only': [],
        'by_record': {}
    }

    # 按记录比较
    for record_id in sorted(all_records):
        as_cds = antismash_by_record.get(record_id, [])
        pk_cds = prokka_by_record.get(record_id, [])

        print(f"\n记录: {record_id}")
        print(f"  antiSMASH: {len(as_cds)} CDS")
        print(f"  Prokka: {len(pk_cds)} CDS")

        # 查找匹配的 CDS（基于位置）
        matched = []
        as_unmatched = []
        pk_unmatched = list(pk_cds)

        for as_cds_item in as_cds:
            found_match = False
            for pk_cds_item in pk_unmatched[:]:
                if as_cds_item.overlaps_with(pk_cds_item, tolerance):
                    matched.append((as_cds_item, pk_cds_item))
                    pk_unmatched.remove(pk_cds_item)
                    found_match = True
                    break

            if not found_match:
                as_unmatched.append(as_cds_item)

        print(f"  匹配: {len(matched)}")
        print(f"  仅 antiSMASH: {len(as_unmatched)}")
        print(f"  仅 Prokka: {len(pk_unmatched)}")

        results['matched'].extend(matched)
        results['antismash_only'].extend(as_unmatched)
        results['prokka_only'].extend(pk_unmatched)
        results['by_record'][record_id] = {
            'antismash_count': len(as_cds),
            'prokka_count': len(pk_cds),
            'matched': len(matched),
            'antismash_only': len(as_unmatched),
            'prokka_only': len(pk_unmatched)
        }

    # 总结
    print(f"\n{'='*60}")
    print(f"总体统计:")
    print(f"  匹配的 CDS 对: {len(results['matched'])}")
    print(f"  仅在 antiSMASH 中: {len(results['antismash_only'])}")
    print(f"  仅在 Prokka 中: {len(results['prokka_only'])}")

    if results['matched']:
        match_rate = len(results['matched']) / max(len(antismash_cds), len(prokka_cds)) * 100
        print(f"  匹配率: {match_rate:.1f}%")

    return results


def generate_detailed_report(results: Dict, output_file: Path = None):
    """生成详细的 Excel 或 CSV 报告"""

    # 准备数据框
    matched_data = []
    for as_cds, pk_cds in results['matched']:
        matched_data.append({
            'record_id': as_cds.record_id,
            'start': as_cds.start,
            'end': as_cds.end,
            'strand': as_cds.strand,
            'as_gene': as_cds.gene,
            'pk_gene': pk_cds.gene,
            'as_locus_tag': as_cds.locus_tag,
            'pk_locus_tag': pk_cds.locus_tag,
            'as_product': as_cds.product,
            'pk_product': pk_cds.product,
            'as_protein_id': as_cds.protein_id,
            'pk_protein_id': pk_cds.protein_id,
            'position_diff': abs(as_cds.start - pk_cds.start) + abs(as_cds.end - pk_cds.end),
            'same_translation': as_cds.translation == pk_cds.translation if as_cds.translation and pk_cds.translation else None
        })

    antismash_only_data = [cds.to_dict() for cds in results['antismash_only']]
    prokka_only_data = [cds.to_dict() for cds in results['prokka_only']]

    # 创建 DataFrame
    df_matched = pd.DataFrame(matched_data) if matched_data else pd.DataFrame()
    df_as_only = pd.DataFrame(antismash_only_data) if antismash_only_data else pd.DataFrame()
    df_pk_only = pd.DataFrame(prokka_only_data) if prokka_only_data else pd.DataFrame()

    # 输出到文件
    if output_file:
        if output_file.suffix == '.xlsx':
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                if not df_matched.empty:
                    df_matched.to_excel(writer, sheet_name='Matched', index=False)
                if not df_as_only.empty:
                    df_as_only.to_excel(writer, sheet_name='antiSMASH_only', index=False)
                if not df_pk_only.empty:
                    df_pk_only.to_excel(writer, sheet_name='Prokka_only', index=False)
            print(f"\n详细报告已保存到: {output_file}")
        else:
            # CSV 格式
            if not df_matched.empty:
                df_matched.to_csv(output_file.parent / f"{output_file.stem}_matched.csv", index=False)
            if not df_as_only.empty:
                df_as_only.to_csv(output_file.parent / f"{output_file.stem}_antismash_only.csv", index=False)
            if not df_pk_only.empty:
                df_pk_only.to_csv(output_file.parent / f"{output_file.stem}_prokka_only.csv", index=False)
            print(f"\n详细报告已保存到: {output_file.parent}/{output_file.stem}_*.csv")

    return df_matched, df_as_only, df_pk_only


def main():
    parser = argparse.ArgumentParser(
        description='比较 antiSMASH 和 Prokka 的 CDS 注释',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 输入选项
    input_group = parser.add_argument_group('输入选项（二选一）')
    input_group.add_argument('--antismash', type=Path, help='antiSMASH GenBank 文件路径')
    input_group.add_argument('--prokka', type=Path, help='Prokka GenBank 文件路径')
    input_group.add_argument('--antismash-dir', type=Path, help='antiSMASH 输出目录路径')
    input_group.add_argument('--prokka-dir', type=Path, help='Prokka 输出目录路径')

    # 其他选项
    parser.add_argument('--tolerance', type=int, default=10,
                       help='位置匹配的容差（碱基对）, 默认: 10')
    parser.add_argument('--output', type=Path,
                       help='输出报告文件路径 (.xlsx 或 .csv)')
    parser.add_argument('--show-details', action='store_true',
                       help='显示详细的不匹配 CDS 列表')

    args = parser.parse_args()

    # 验证输入参数
    if args.antismash and args.antismash_dir:
        parser.error("不能同时指定 --antismash 和 --antismash-dir")
    if args.prokka and args.prokka_dir:
        parser.error("不能同时指定 --prokka 和 --prokka-dir")

    if not ((args.antismash or args.antismash_dir) and (args.prokka or args.prokka_dir)):
        parser.error("必须指定 antiSMASH 和 Prokka 的输入（文件或目录）")

    # 提取 CDS
    print("正在提取 antiSMASH CDS 注释...")
    if args.antismash:
        antismash_cds = extract_cds_from_gbk(args.antismash, 'antismash')
    else:
        antismash_cds = extract_cds_from_directory(args.antismash_dir, 'antismash')

    print(f"\n正在提取 Prokka CDS 注释...")
    if args.prokka:
        prokka_cds = extract_cds_from_gbk(args.prokka, 'prokka')
    else:
        prokka_cds = extract_cds_from_directory(args.prokka_dir, 'prokka')

    if not antismash_cds or not prokka_cds:
        print("\n错误：未能提取到 CDS 注释", file=sys.stderr)
        sys.exit(1)

    # 比较
    results = compare_cds_lists(antismash_cds, prokka_cds, args.tolerance)

    # 显示详细信息
    if args.show_details:
        if results['antismash_only']:
            print(f"\n{'='*60}")
            print("仅在 antiSMASH 中的 CDS:")
            for cds in results['antismash_only'][:20]:  # 限制显示数量
                print(f"  {cds}")
            if len(results['antismash_only']) > 20:
                print(f"  ... 还有 {len(results['antismash_only']) - 20} 个")

        if results['prokka_only']:
            print(f"\n{'='*60}")
            print("仅在 Prokka 中的 CDS:")
            for cds in results['prokka_only'][:20]:
                print(f"  {cds}")
            if len(results['prokka_only']) > 20:
                print(f"  ... 还有 {len(results['prokka_only']) - 20} 个")

    # 生成报告
    if args.output:
        try:
            generate_detailed_report(results, args.output)
        except Exception as e:
            print(f"\n警告：无法生成详细报告: {e}", file=sys.stderr)
            print("提示：安装 pandas 和 openpyxl 以生成 Excel 报告:")
            print("  pip install pandas openpyxl")

    print(f"\n{'='*60}\n")


if __name__ == '__main__':
    main()

