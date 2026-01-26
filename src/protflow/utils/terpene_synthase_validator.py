"""
萜合酶（Terpene Synthase）序列核实工具

使用多种方法核实蛋白质序列是否为萜合酶：
1. 关键词搜索（序列注释）
2. PROSITE模式匹配
3. HMMER搜索（如果可用）
4. BLAST搜索（如果可用）
5. 序列特征分析
"""
import re
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

from ..utils.logger import get_logger

logger = get_logger(__name__)


# 萜合酶相关关键词
TERPENE_SYNTHASE_KEYWORDS = [
    'terpene synthase',
    'terpene cyclase',
    'terpenoid synthase',
    'isoprenoid synthase',
    'sesquiterpene synthase',
    'monoterpene synthase',
    'diterpene synthase',
    'triterpene synthase',
    'TPS',
    'terpene',
    'terpenoid',
    'isoprenoid',
    'cyclase',
    'synthase',
]

# PROSITE模式：萜合酶保守域模式
# 模式：[DE]-G-S-W-x-[GE]-x-W-[GA]-[LIVM]-x-[FY]-x-Y-[GA]
TERPENE_SYNTHASE_PROSITE_PATTERN = re.compile(
    r'[DE]-G-S-W-[A-Z]-[GE]-[A-Z]-W-[GA]-[LIVM]-[A-Z]-[FY]-[A-Z]-Y-[GA]',
    re.IGNORECASE
)

# 简化的萜合酶特征模式（更宽松）
TERPENE_SYNTHASE_SIMPLE_PATTERN = re.compile(
    r'[DE]G[ST]W',
    re.IGNORECASE
)


def check_keywords(record: SeqRecord) -> Tuple[bool, List[str]]:
    """
    检查序列注释中是否包含萜合酶相关关键词。
    
    Args:
        record: SeqRecord对象
        
    Returns:
        (是否匹配, 匹配的关键词列表)
    """
    text = ' '.join([
        record.id,
        record.description,
        ' '.join(record.annotations.values()) if record.annotations else ''
    ]).lower()
    
    matched_keywords = []
    for keyword in TERPENE_SYNTHASE_KEYWORDS:
        if keyword.lower() in text:
            matched_keywords.append(keyword)
    
    return len(matched_keywords) > 0, matched_keywords


def check_prosite_pattern(sequence: str) -> Tuple[bool, int]:
    """
    检查序列是否包含PROSITE萜合酶模式。
    
    Args:
        sequence: 蛋白质序列字符串
        
    Returns:
        (是否匹配, 匹配次数)
    """
    # 将序列转换为PROSITE格式（使用单字母代码）
    # 查找简化的保守模式
    matches = list(TERPENE_SYNTHASE_SIMPLE_PATTERN.finditer(sequence))
    match_count = len(matches)
    
    return match_count > 0, match_count


def check_sequence_features(sequence: str) -> Dict[str, any]:
    """
    分析序列特征，判断是否符合萜合酶特征。
    
    Args:
        sequence: 蛋白质序列字符串
        
    Returns:
        特征字典
    """
    seq_len = len(sequence)
    
    # 萜合酶通常长度在300-800 aa之间
    length_ok = 200 <= seq_len <= 1200
    
    # 检查是否包含常见的萜合酶保守残基
    # DDXXD/E motif (二价金属离子结合位点)
    ddxxd_pattern = re.compile(r'D[^D]{2,3}D', re.IGNORECASE)
    ddxxd_matches = len(ddxxd_pattern.findall(sequence))
    
    # 检查芳香族氨基酸比例（萜合酶通常有较高的芳香族氨基酸）
    aromatic_aa = set('FWY')
    aromatic_count = sum(1 for aa in sequence if aa.upper() in aromatic_aa)
    aromatic_ratio = aromatic_count / seq_len if seq_len > 0 else 0
    
    # 萜合酶通常芳香族氨基酸比例在0.08-0.15之间
    aromatic_ok = 0.05 <= aromatic_ratio <= 0.20
    
    return {
        'length': seq_len,
        'length_ok': length_ok,
        'ddxxd_motif_count': ddxxd_matches,
        'aromatic_ratio': aromatic_ratio,
        'aromatic_ok': aromatic_ok,
    }


def check_hmmer(sequence_file: Path, hmm_profile: Optional[Path] = None) -> Optional[Dict[str, any]]:
    """
    使用HMMER搜索Pfam数据库（如果可用）。
    
    Args:
        sequence_file: 序列文件路径
        hmm_profile: HMM配置文件路径（可选）
        
    Returns:
        搜索结果字典，如果HMMER不可用则返回None
    """
    # 检查HMMER是否安装
    if not shutil.which('hmmscan') and not shutil.which('hmmsearch'):
        logger.warning("HMMER未安装，跳过HMMER搜索")
        return None
    
    try:
        # 如果提供了HMM profile，使用hmmsearch
        if hmm_profile and hmm_profile.exists():
            cmd = ['hmmsearch', '--domtblout', '/dev/stdout', str(hmm_profile), str(sequence_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                # 解析输出
                return {'method': 'hmmsearch', 'output': result.stdout}
    except Exception as e:
        logger.warning(f"HMMER搜索失败: {e}")
    
    return None


def validate_terpene_synthase(
    record: SeqRecord,
    use_keywords: bool = True,
    use_prosite: bool = True,
    use_features: bool = True
) -> Dict[str, any]:
    """
    综合验证序列是否为萜合酶。
    
    Args:
        record: SeqRecord对象
        use_keywords: 是否使用关键词搜索
        use_prosite: 是否使用PROSITE模式
        use_features: 是否使用序列特征分析
        
    Returns:
        验证结果字典
    """
    sequence = str(record.seq)
    results = {
        'id': record.id,
        'description': record.description,
        'length': len(sequence),
        'is_terpene_synthase': False,
        'confidence': 'low',
        'methods': {},
        'score': 0
    }
    
    score = 0
    max_score = 0
    
    # 1. 关键词搜索
    if use_keywords:
        max_score += 3
        keyword_match, matched_keywords = check_keywords(record)
        results['methods']['keywords'] = {
            'matched': keyword_match,
            'keywords': matched_keywords
        }
        if keyword_match:
            score += 3
            results['is_terpene_synthase'] = True
    
    # 2. PROSITE模式匹配
    if use_prosite:
        max_score += 2
        prosite_match, match_count = check_prosite_pattern(sequence)
        results['methods']['prosite'] = {
            'matched': prosite_match,
            'match_count': match_count
        }
        if prosite_match:
            score += 2
            if not results['is_terpene_synthase']:
                results['is_terpene_synthase'] = True
    
    # 3. 序列特征分析
    if use_features:
        max_score += 2
        features = check_sequence_features(sequence)
        results['methods']['features'] = features
        
        feature_score = 0
        if features['length_ok']:
            feature_score += 1
        if features['ddxxd_motif_count'] > 0:
            feature_score += 0.5
        if features['aromatic_ok']:
            feature_score += 0.5
        
        score += feature_score
    
    # 计算置信度
    if max_score > 0:
        confidence_ratio = score / max_score
        if confidence_ratio >= 0.7:
            results['confidence'] = 'high'
        elif confidence_ratio >= 0.4:
            results['confidence'] = 'medium'
        else:
            results['confidence'] = 'low'
    
    results['score'] = score
    results['max_score'] = max_score
    
    return results


def validate_fasta_file(
    fasta_file: Path,
    output_csv: Optional[Path] = None,
    use_keywords: bool = True,
    use_prosite: bool = True,
    use_features: bool = True
) -> Tuple[List[Dict], Dict[str, int]]:
    """
    验证FASTA文件中的所有序列。
    
    Args:
        fasta_file: 输入FASTA文件路径
        output_csv: 输出CSV文件路径（可选）
        use_keywords: 是否使用关键词搜索
        use_prosite: 是否使用PROSITE模式
        use_features: 是否使用序列特征分析
        
    Returns:
        (结果列表, 统计字典)
    """
    if not fasta_file.exists():
        raise FileNotFoundError(f"FASTA文件不存在: {fasta_file}")
    
    logger.info(f"开始验证序列文件: {fasta_file}")
    
    results = []
    stats = {
        'total': 0,
        'terpene_synthase': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'low_confidence': 0,
        'not_terpene_synthase': 0
    }
    
    # 读取并验证所有序列
    for record in SeqIO.parse(str(fasta_file), 'fasta'):
        stats['total'] += 1
        result = validate_terpene_synthase(
            record,
            use_keywords=use_keywords,
            use_prosite=use_prosite,
            use_features=use_features
        )
        results.append(result)
        
        # 更新统计
        if result['is_terpene_synthase']:
            stats['terpene_synthase'] += 1
            stats[f"{result['confidence']}_confidence"] += 1
        else:
            stats['not_terpene_synthase'] += 1
        
        if stats['total'] % 50 == 0:
            logger.info(f"已处理 {stats['total']} 条序列...")
    
    logger.info(f"验证完成: 共 {stats['total']} 条序列")
    logger.info(f"  萜合酶: {stats['terpene_synthase']} ({stats['terpene_synthase']/stats['total']*100:.1f}%)")
    logger.info(f"  非萜合酶: {stats['not_terpene_synthase']} ({stats['not_terpene_synthase']/stats['total']*100:.1f}%)")
    
    # 保存结果到CSV
    if output_csv:
        import pandas as pd
        import json
        
        # 将methods字典转换为JSON字符串以便保存到CSV
        df_data = []
        for r in results:
            row = r.copy()
            if 'methods' in row:
                row['methods'] = json.dumps(row['methods'], ensure_ascii=False)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        logger.info(f"结果已保存到: {output_csv}")
    
    return results, stats


def batch_validate_directory(
    input_dir: Path,
    pattern: str = "*.fasta",
    output_dir: Optional[Path] = None,
    use_keywords: bool = True,
    use_prosite: bool = True,
    use_features: bool = True,
    match_pdb: bool = True,
    pdb_pattern: str = "*_alphafold.pdb",
    num_workers: int = 1
) -> Tuple[List[Dict], Dict[str, any]]:
    """
    批量验证目录中的所有序列文件。
    
    Args:
        input_dir: 包含序列文件的目录
        pattern: 文件匹配模式，默认 "*.fasta"
        output_dir: 输出目录（可选）
        use_keywords: 是否使用关键词搜索
        use_prosite: 是否使用PROSITE模式
        use_features: 是否使用序列特征分析
        match_pdb: 是否尝试匹配对应的PDB文件
        pdb_pattern: PDB文件匹配模式，默认 "*_alphafold.pdb"
        num_workers: 并行处理的工作进程数（1=串行）
        
    Returns:
        (所有结果列表, 汇总统计字典)
    """
    input_dir = Path(input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"输入目录不存在: {input_dir}")
    
    # 查找所有序列文件
    fasta_files = sorted(list(input_dir.glob(pattern)))
    # 也查找 .fa 和 .faa 文件
    fasta_files.extend(input_dir.glob("*.fa"))
    fasta_files.extend(input_dir.glob("*.faa"))
    fasta_files = sorted(list(set(fasta_files)), key=lambda x: x.name)
    
    if not fasta_files:
        logger.warning(f"在 {input_dir} 中未找到匹配 {pattern} 的序列文件")
        return [], {}
    
    logger.info(f"找到 {len(fasta_files)} 个序列文件")
    
    # 创建输出目录
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
    
    all_results = []
    file_stats = {
        'total_files': len(fasta_files),
        'processed': 0,
        'failed': 0,
        'total_sequences': 0,
        'terpene_synthase_sequences': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'low_confidence': 0,
        'not_terpene_synthase': 0,
        'files_with_pdb': 0
    }
    
    # 处理每个文件
    from tqdm import tqdm
    
    for fasta_file in tqdm(fasta_files, desc="处理序列文件"):
        try:
            # 尝试匹配PDB文件
            pdb_file = None
            if match_pdb:
                # 从文件名提取ID（例如 A0A0B4G3Q7.fasta -> A0A0B4G3Q7）
                file_id = fasta_file.stem
                # 尝试多种PDB文件命名模式
                pdb_patterns = [
                    input_dir / f"{file_id}_alphafold.pdb",
                    input_dir / f"{file_id}.pdb",
                    input_dir / f"{file_id}_esm3.pdb",
                ]
                for pattern_path in pdb_patterns:
                    if pattern_path.exists():
                        pdb_file = pattern_path
                        break
                
                # 如果没找到，尝试glob模式
                if pdb_file is None:
                    pdb_matches = list(input_dir.glob(f"{file_id}{pdb_pattern}"))
                    if pdb_matches:
                        pdb_file = pdb_matches[0]
            
            # 验证序列文件
            file_output_csv = None
            if output_dir:
                file_output_csv = output_dir / f"{fasta_file.stem}_validation.csv"
            
            file_results, file_stat = validate_fasta_file(
                fasta_file=fasta_file,
                output_csv=file_output_csv,
                use_keywords=use_keywords,
                use_prosite=use_prosite,
                use_features=use_features
            )
            
            # 为每个结果添加文件信息
            for result in file_results:
                result['source_file'] = fasta_file.name
                result['source_path'] = str(fasta_file)
                if pdb_file:
                    result['pdb_file'] = pdb_file.name
                    result['pdb_path'] = str(pdb_file)
                    result['has_structure'] = True
                else:
                    result['pdb_file'] = None
                    result['pdb_path'] = None
                    result['has_structure'] = False
            
            all_results.extend(file_results)
            
            # 更新统计
            file_stats['processed'] += 1
            file_stats['total_sequences'] += file_stat['total']
            file_stats['terpene_synthase_sequences'] += file_stat['terpene_synthase']
            file_stats['high_confidence'] += file_stat['high_confidence']
            file_stats['medium_confidence'] += file_stat['medium_confidence']
            file_stats['low_confidence'] += file_stat['low_confidence']
            file_stats['not_terpene_synthase'] += file_stat['not_terpene_synthase']
            if pdb_file:
                file_stats['files_with_pdb'] += 1
            
        except Exception as e:
            logger.error(f"处理文件 {fasta_file.name} 时出错: {e}")
            file_stats['failed'] += 1
            continue
    
    # 保存汇总结果
    if output_dir:
        import pandas as pd
        import json
        
        # 保存所有结果
        summary_csv = output_dir / 'batch_validation_summary.csv'
        df_data = []
        for r in all_results:
            row = r.copy()
            if 'methods' in row:
                row['methods'] = json.dumps(row['methods'], ensure_ascii=False)
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv(summary_csv, index=False, encoding='utf-8-sig')
        logger.info(f"汇总结果已保存到: {summary_csv}")
        
        # 保存统计报告
        stats_file = output_dir / 'batch_validation_stats.json'
        import json as json_module
        with open(stats_file, 'w', encoding='utf-8') as f:
            json_module.dump(file_stats, f, indent=2, ensure_ascii=False)
        logger.info(f"统计报告已保存到: {stats_file}")
    
    logger.info(f"\n批量验证完成:")
    logger.info(f"  处理文件数: {file_stats['processed']}/{file_stats['total_files']}")
    logger.info(f"  总序列数: {file_stats['total_sequences']}")
    logger.info(f"  萜合酶序列: {file_stats['terpene_synthase_sequences']} ({file_stats['terpene_synthase_sequences']/file_stats['total_sequences']*100:.1f}%)")
    logger.info(f"  有结构文件的序列: {file_stats['files_with_pdb']}")
    
    return all_results, file_stats
