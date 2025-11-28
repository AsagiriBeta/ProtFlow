"""
CDS 注释比较工具 - 比较 antiSMASH 和 Prokka 的输出

该模块提供了在 Jupyter Notebook 中比较 CDS 注释的便捷函数
"""

from pathlib import Path
from typing import List, Dict
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature
from collections import defaultdict

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CDSFeature:
    """CDS 特征的简化表示"""

    def __init__(self, feature: SeqFeature, record_id: str, source: str):
        self.record_id = record_id
        self.source = source
        self.start = int(feature.location.start)
        self.end = int(feature.location.end)
        self.strand = feature.location.strand
        self.length = self.end - self.start

        # 提取注释信息
        q = feature.qualifiers
        self.gene = q.get('gene', [''])[0]
        self.locus_tag = q.get('locus_tag', [''])[0]
        self.product = q.get('product', [''])[0]
        self.protein_id = q.get('protein_id', [''])[0]
        self.translation = q.get('translation', [''])[0]

    def __repr__(self):
        return f"{self.source}:{self.record_id}[{self.start}:{self.end}]({self.gene or self.locus_tag})"

    def matches_location(self, other: 'CDSFeature', tolerance: int = 10) -> bool:
        """检查位置是否匹配（允许一定容差）"""
        if self.strand != other.strand:
            return False
        return (abs(self.start - other.start) <= tolerance and
                abs(self.end - other.end) <= tolerance)


def extract_cds_from_gbk(gbk_path: Path, source: str = 'unknown') -> List[CDSFeature]:
    """从 GenBank 文件提取 CDS 特征"""
    cds_features = []

    try:
        for record in SeqIO.parse(str(gbk_path), 'genbank'):
            for feature in record.features:
                if feature.type == 'CDS':
                    cds_features.append(CDSFeature(feature, record.id, source))
        logger.info(f"从 {gbk_path.name} 提取了 {len(cds_features)} 个 CDS")
    except Exception as e:
        logger.error(f"解析 {gbk_path} 失败: {e}")

    return cds_features


def extract_cds_from_dir(directory: Path, source: str = 'unknown') -> List[CDSFeature]:
    """从目录中的所有 GenBank 文件提取 CDS"""
    all_cds = []
    gbk_files = list(directory.glob('**/*.gbk')) + list(directory.glob('**/*.gbff'))

    for gbk_file in gbk_files:
        cds_list = extract_cds_from_gbk(gbk_file, source)
        all_cds.extend(cds_list)

    logger.info(f"从 {directory} 总共提取了 {len(all_cds)} 个 CDS (来自 {len(gbk_files)} 个文件)")
    return all_cds


def compare_cds(antismash_cds: List[CDSFeature],
                prokka_cds: List[CDSFeature],
                tolerance: int = 10) -> Dict:
    """
    比较两组 CDS 注释

    Args:
        antismash_cds: antiSMASH 的 CDS 列表
        prokka_cds: Prokka 的 CDS 列表
        tolerance: 位置匹配的容差（碱基对）

    Returns:
        包含比较结果的字典
    """
    # 按 record_id 分组
    as_by_record = defaultdict(list)
    pk_by_record = defaultdict(list)

    for cds in antismash_cds:
        as_by_record[cds.record_id].append(cds)
    for cds in prokka_cds:
        pk_by_record[cds.record_id].append(cds)

    all_records = set(as_by_record.keys()) | set(pk_by_record.keys())

    matched_pairs = []
    as_only = []
    pk_only = []
    record_stats = {}

    # 逐个记录比较
    for record_id in all_records:
        as_list = as_by_record.get(record_id, [])
        pk_list = pk_by_record.get(record_id, [])

        # 按位置排序
        as_list.sort(key=lambda x: x.start)
        pk_list.sort(key=lambda x: x.start)

        # 匹配 CDS
        pk_remaining = pk_list.copy()
        record_matched = []
        record_as_only = []

        for as_cds in as_list:
            found = False
            for pk_cds in pk_remaining:
                if as_cds.matches_location(pk_cds, tolerance):
                    matched_pairs.append((as_cds, pk_cds))
                    record_matched.append((as_cds, pk_cds))
                    pk_remaining.remove(pk_cds)
                    found = True
                    break
            if not found:
                as_only.append(as_cds)
                record_as_only.append(as_cds)

        pk_only.extend(pk_remaining)

        record_stats[record_id] = {
            'antismash_total': len(as_list),
            'prokka_total': len(pk_list),
            'matched': len(record_matched),
            'antismash_only': len(record_as_only),
            'prokka_only': len(pk_remaining)
        }

    return {
        'matched': matched_pairs,
        'antismash_only': as_only,
        'prokka_only': pk_only,
        'record_stats': record_stats,
        'summary': {
            'total_antismash': len(antismash_cds),
            'total_prokka': len(prokka_cds),
            'total_matched': len(matched_pairs),
            'total_antismash_only': len(as_only),
            'total_prokka_only': len(pk_only),
            'match_rate': len(matched_pairs) / max(len(antismash_cds), len(prokka_cds)) * 100 if antismash_cds or prokka_cds else 0
        }
    }


def print_comparison_report(results: Dict, verbose: bool = False):
    """打印比较报告"""
    summary = results['summary']

    print("=" * 70)
    print("CDS 注释比较报告")
    print("=" * 70)
    print(f"\n总体统计:")
    print(f"  antiSMASH CDS 总数: {summary['total_antismash']}")
    print(f"  Prokka CDS 总数:    {summary['total_prokka']}")
    print(f"  匹配的 CDS 对数:    {summary['total_matched']}")
    print(f"  仅 antiSMASH:       {summary['total_antismash_only']}")
    print(f"  仅 Prokka:          {summary['total_prokka_only']}")
    print(f"  匹配率:             {summary['match_rate']:.1f}%")

    if results['record_stats']:
        print(f"\n按记录统计:")
        for record_id, stats in results['record_stats'].items():
            print(f"\n  {record_id}:")
            print(f"    antiSMASH: {stats['antismash_total']}, Prokka: {stats['prokka_total']}, 匹配: {stats['matched']}")
            if stats['antismash_only'] > 0:
                print(f"    仅 antiSMASH: {stats['antismash_only']}")
            if stats['prokka_only'] > 0:
                print(f"    仅 Prokka: {stats['prokka_only']}")

    if verbose:
        if results['antismash_only']:
            print(f"\n仅在 antiSMASH 中的 CDS (显示前 10 个):")
            for cds in results['antismash_only'][:10]:
                print(f"  {cds.start:8d}-{cds.end:8d} ({cds.length:5d}bp) {cds.product[:50]}")

        if results['prokka_only']:
            print(f"\n仅在 Prokka 中的 CDS (显示前 10 个):")
            for cds in results['prokka_only'][:10]:
                print(f"  {cds.start:8d}-{cds.end:8d} ({cds.length:5d}bp) {cds.product[:50]}")

    print("=" * 70)


def compare_annotations(antismash_path: Path,
                       prokka_path: Path,
                       tolerance: int = 10,
                       verbose: bool = True) -> Dict:
    """
    便捷函数：比较 antiSMASH 和 Prokka 的注释结果

    Args:
        antismash_path: antiSMASH 输出文件或目录路径
        prokka_path: Prokka 输出文件或目录路径
        tolerance: 位置匹配容差（碱基对）
        verbose: 是否打印详细报告

    Returns:
        比较结果字典
    """
    logger.info(f"比较 antiSMASH 和 Prokka 的 CDS 注释")
    logger.info(f"antiSMASH: {antismash_path}")
    logger.info(f"Prokka: {prokka_path}")

    # 提取 CDS
    if antismash_path.is_file():
        as_cds = extract_cds_from_gbk(antismash_path, 'antismash')
    else:
        as_cds = extract_cds_from_dir(antismash_path, 'antismash')

    if prokka_path.is_file():
        pk_cds = extract_cds_from_gbk(prokka_path, 'prokka')
    else:
        pk_cds = extract_cds_from_dir(prokka_path, 'prokka')

    if not as_cds:
        logger.warning("未从 antiSMASH 提取到 CDS")
    if not pk_cds:
        logger.warning("未从 Prokka 提取到 CDS")

    # 比较
    results = compare_cds(as_cds, pk_cds, tolerance)

    # 打印报告
    if verbose:
        print_comparison_report(results, verbose=verbose)

    return results


def export_comparison_to_csv(results: Dict, output_prefix: Path):
    """
    将比较结果导出为 CSV 文件

    Args:
        results: compare_cds 返回的结果字典
        output_prefix: 输出文件前缀（不含扩展名）
    """
    try:
        import pandas as pd
    except ImportError:
        logger.warning("需要安装 pandas 才能导出 CSV: pip install pandas")
        return

    output_prefix = Path(output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    # 匹配的 CDS
    if results['matched']:
        matched_data = []
        for as_cds, pk_cds in results['matched']:
            matched_data.append({
                'record_id': as_cds.record_id,
                'start': as_cds.start,
                'end': as_cds.end,
                'length': as_cds.length,
                'strand': '+' if as_cds.strand == 1 else '-' if as_cds.strand == -1 else '.',
                'as_gene': as_cds.gene,
                'pk_gene': pk_cds.gene,
                'as_locus_tag': as_cds.locus_tag,
                'pk_locus_tag': pk_cds.locus_tag,
                'as_product': as_cds.product,
                'pk_product': pk_cds.product,
                'position_diff': abs(as_cds.start - pk_cds.start) + abs(as_cds.end - pk_cds.end),
                'same_sequence': as_cds.translation == pk_cds.translation if as_cds.translation and pk_cds.translation else None
            })
        pd.DataFrame(matched_data).to_csv(f"{output_prefix}_matched.csv", index=False)
        logger.info(f"匹配的 CDS 已导出到 {output_prefix}_matched.csv")

    # 仅 antiSMASH
    if results['antismash_only']:
        as_data = [{
            'record_id': cds.record_id,
            'start': cds.start,
            'end': cds.end,
            'length': cds.length,
            'gene': cds.gene,
            'locus_tag': cds.locus_tag,
            'product': cds.product
        } for cds in results['antismash_only']]
        pd.DataFrame(as_data).to_csv(f"{output_prefix}_antismash_only.csv", index=False)
        logger.info(f"仅 antiSMASH 的 CDS 已导出到 {output_prefix}_antismash_only.csv")

    # 仅 Prokka
    if results['prokka_only']:
        pk_data = [{
            'record_id': cds.record_id,
            'start': cds.start,
            'end': cds.end,
            'length': cds.length,
            'gene': cds.gene,
            'locus_tag': cds.locus_tag,
            'product': cds.product
        } for cds in results['prokka_only']]
        pd.DataFrame(pk_data).to_csv(f"{output_prefix}_prokka_only.csv", index=False)
        logger.info(f"仅 Prokka 的 CDS 已导出到 {output_prefix}_prokka_only.csv")

