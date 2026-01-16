"""
结构分析和批量处理模块

提供结构质量评估、相似性分析、聚类等功能。
"""

import re
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from Bio.PDB import PDBParser, PDBIO, Superimposer
from Bio.PDB.PDBExceptions import PDBConstructionException

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

from ..utils.logger import get_logger

logger = get_logger(__name__)


def collect_structure_files(input_path: Path) -> List[Dict]:
    """
    收集结构文件
    
    Args:
        input_path: 输入路径（文件或目录）
    
    Returns:
        结构文件信息列表
    """
    input_path = Path(input_path)
    structure_files = []
    
    if input_path.is_file():
        if input_path.suffix.lower() == '.pdb':
            structure_files.append(input_path)
            logger.info(f"找到单个文件: {input_path.name}")
        else:
            logger.warning(f"不支持的文件格式: {input_path.suffix}")
    
    elif input_path.is_dir():
        pdb_files = list(input_path.glob('*.pdb'))
        pdb_files.extend(input_path.glob('*.PDB'))
        
        if len(pdb_files) < 10:
            pdb_files.extend(input_path.rglob('*.pdb'))
            pdb_files.extend(input_path.rglob('*.PDB'))
        
        pdb_files = sorted(list(set(pdb_files)), key=lambda x: x.name)
        structure_files = pdb_files
        logger.info(f"在目录中找到 {len(structure_files)} 个PDB文件")
    
    else:
        logger.error(f"路径不存在: {input_path}")
        return []
    
    # 验证文件并提取信息
    protein_info = []
    for pdb_file in structure_files:
        if pdb_file.exists() and pdb_file.stat().st_size > 0:
            protein_name = re.sub(r'[^\w\-_.]', '_', pdb_file.stem)
            protein_info.append({
                'file_path': str(pdb_file),
                'file_name': pdb_file.name,
                'protein_name': protein_name,
                'file_size': pdb_file.stat().st_size
            })
        else:
            logger.warning(f"跳过无效文件: {pdb_file}")
    
    logger.info(f"有效文件: {len(protein_info)} 个")
    return protein_info


def assess_structure_quality(pdb_file: Path) -> Dict:
    """
    评估单个结构的质量
    
    Args:
        pdb_file: PDB文件路径
    
    Returns:
        质量评估结果字典
    """
    quality_metrics = {
        'file_path': str(pdb_file),
        'file_name': pdb_file.name,
        'status': 'failed',
        'num_models': 0,
        'num_chains': 0,
        'num_residues': 0,
        'num_atoms': 0,
        'residue_types': [],
        'error_message': None
    }
    
    try:
        parser = PDBParser(PERMISSIVE=1, QUIET=1)
        structure = parser.get_structure('temp', pdb_file)
        
        quality_metrics['status'] = 'success'
        quality_metrics['num_models'] = len(structure)
        
        chains = []
        residues = []
        atoms = []
        residue_types = set()
        
        for model in structure:
            for chain in model:
                chains.append(chain.id)
                for residue in chain:
                    residues.append(residue.id[1])
                    residue_types.add(residue.resname)
                    for atom in residue:
                        atoms.append(atom.name)
        
        quality_metrics['num_chains'] = len(set(chains))
        quality_metrics['num_residues'] = len(residues)
        quality_metrics['num_atoms'] = len(atoms)
        quality_metrics['residue_types'] = list(residue_types)
        
        if quality_metrics['num_residues'] < 10:
            quality_metrics['status'] = 'poor'
            quality_metrics['error_message'] = '残基数过少'
        elif quality_metrics['num_atoms'] < quality_metrics['num_residues'] * 5:
            quality_metrics['status'] = 'incomplete'
            quality_metrics['error_message'] = '原子数不足，可能结构不完整'
        
    except PDBConstructionException as e:
        quality_metrics['error_message'] = f"PDB格式错误: {str(e)}"
    except Exception as e:
        quality_metrics['error_message'] = f"解析错误: {str(e)}"
    
    return quality_metrics


def batch_quality_assessment(structure_info: List[Dict]) -> List[Dict]:
    """
    批量质量评估
    
    Args:
        structure_info: 结构文件信息列表
    
    Returns:
        质量评估结果列表
    """
    from tqdm import tqdm
    
    logger.info(f"开始评估 {len(structure_info)} 个结构")
    
    quality_results = []
    for info in tqdm(structure_info, desc="质量评估"):
        quality = assess_structure_quality(Path(info['file_path']))
        quality.update(info)
        quality_results.append(quality)
    
    # 统计
    status_counts = {}
    successful_structures = 0
    total_residues = 0
    total_atoms = 0
    
    for result in quality_results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if result['status'] == 'success':
            successful_structures += 1
            total_residues += result['num_residues']
            total_atoms += result['num_atoms']
    
    logger.info(f"评估完成: 成功 {successful_structures}, 失败 {len(quality_results) - successful_structures}")
    
    if successful_structures > 0:
        logger.info(f"平均残基数: {total_residues / successful_structures:.1f}")
        logger.info(f"平均原子数: {total_atoms / successful_structures:.1f}")
    
    return quality_results


def calculate_structure_similarity(pdb_file1: Path, pdb_file2: Path) -> Dict:
    """
    计算两个结构之间的相似性
    
    Args:
        pdb_file1: 第一个PDB文件
        pdb_file2: 第二个PDB文件
    
    Returns:
        相似性结果字典
    """
    try:
        parser = PDBParser(PERMISSIVE=1, QUIET=1)
        
        structure1 = parser.get_structure('s1', pdb_file1)
        structure2 = parser.get_structure('s2', pdb_file2)
        
        atoms1 = []
        atoms2 = []
        
        for model in structure1:
            for chain in model:
                for residue in chain:
                    if residue.has_id('CA'):
                        atoms1.append(residue['CA'])
        
        for model in structure2:
            for chain in model:
                for residue in chain:
                    if residue.has_id('CA'):
                        atoms2.append(residue['CA'])
        
        if len(atoms1) == 0 or len(atoms2) == 0:
            return {
                'rmsd': None,
                'similarity_score': 0,
                'common_residues': 0,
                'length_ratio': 0,
                'status': 'no_common_atoms'
            }
        
        min_length = min(len(atoms1), len(atoms2))
        atoms1 = atoms1[:min_length]
        atoms2 = atoms2[:min_length]
        
        sup = Superimposer()
        sup.set_atoms(atoms1, atoms2)
        rmsd = sup.rms
        
        if rmsd is not None:
            if rmsd < 2.0:
                similarity_score = 1.0 - (rmsd / 2.0) * 0.5
            elif rmsd < 4.0:
                similarity_score = 0.5 - ((rmsd - 2.0) / 2.0) * 0.4
            else:
                similarity_score = 0.1 - min((rmsd - 4.0) / 6.0, 0.09)
            
            similarity_score = max(0.01, similarity_score)
        else:
            similarity_score = 0
        
        return {
            'rmsd': rmsd,
            'similarity_score': similarity_score,
            'common_residues': min_length,
            'length_ratio': min_length / max(len(atoms1), len(atoms2)),
            'status': 'success'
        }
    
    except Exception as e:
        return {
            'rmsd': None,
            'similarity_score': 0,
            'common_residues': 0,
            'length_ratio': 0,
            'status': f'error: {str(e)}'
        }


def batch_similarity_analysis(quality_results: List[Dict]) -> Optional[Dict]:
    """
    批量相似性分析
    
    Args:
        quality_results: 质量评估结果列表
    
    Returns:
        相似性分析结果字典
    """
    successful_structures = [
        r for r in quality_results
        if r['status'] == 'success' and r['num_residues'] >= 30
    ]
    
    if len(successful_structures) < 2:
        logger.warning(f"需要至少2个有效结构进行分析，当前有 {len(successful_structures)} 个")
        return None
    
    logger.info(f"开始分析 {len(successful_structures)} 个结构的相似性")
    
    n_structures = len(successful_structures)
    similarity_matrix = np.zeros((n_structures, n_structures))
    rmsd_matrix = np.full((n_structures, n_structures), np.nan)
    
    similarity_results = []
    
    from tqdm import tqdm
    
    with tqdm(total=n_structures * (n_structures - 1) // 2, desc="相似性计算") as pbar:
        for i in range(n_structures):
            for j in range(i + 1, n_structures):
                result = calculate_structure_similarity(
                    Path(successful_structures[i]['file_path']),
                    Path(successful_structures[j]['file_path'])
                )
                
                similarity_matrix[i, j] = result['similarity_score']
                similarity_matrix[j, i] = result['similarity_score']
                
                if result['rmsd'] is not None:
                    rmsd_matrix[i, j] = result['rmsd']
                    rmsd_matrix[j, i] = result['rmsd']
                
                similarity_results.append({
                    'structure1': successful_structures[i]['protein_name'],
                    'structure2': successful_structures[j]['protein_name'],
                    'rmsd': result['rmsd'],
                    'similarity_score': result['similarity_score'],
                    'common_residues': result['common_residues'],
                    'status': result['status']
                })
                
                pbar.update(1)
    
    np.fill_diagonal(similarity_matrix, 1.0)
    np.fill_diagonal(rmsd_matrix, 0.0)
    
    structure_names = [s['protein_name'] for s in successful_structures]
    
    result_dict = {
        'similarity_matrix': similarity_matrix,
        'rmsd_matrix': rmsd_matrix,
        'structure_names': structure_names,
        'similarity_results': similarity_results
    }
    
    if HAS_PANDAS:
        result_dict['similarity_matrix_df'] = pd.DataFrame(
            similarity_matrix,
            index=structure_names,
            columns=structure_names
        )
        result_dict['rmsd_matrix_df'] = pd.DataFrame(
            rmsd_matrix,
            index=structure_names,
            columns=structure_names
        )
        result_dict['similarity_results_df'] = pd.DataFrame(similarity_results)
    
    logger.info("相似性分析完成")
    return result_dict


def perform_clustering_analysis(similarity_data: Dict) -> Optional[Dict]:
    """
    执行聚类分析
    
    Args:
        similarity_data: 相似性分析结果
    
    Returns:
        聚类结果字典
    """
    try:
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.decomposition import PCA
    except ImportError:
        logger.warning("需要安装 scikit-learn 进行聚类分析: pip install scikit-learn")
        return None
    
    similarity_matrix = similarity_data['similarity_matrix']
    distance_matrix = 1 - similarity_matrix
    
    n_samples = len(similarity_data['structure_names'])
    
    if n_samples < 3:
        logger.warning(f"样本数过少 ({n_samples})，无法进行有意义的聚类")
        return None
    
    best_n_clusters = 2
    best_score = -1
    best_labels = None
    
    for n_clusters in range(2, min(n_samples, 8)):
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='precomputed',
            linkage='average'
        )
        
        labels = clustering.fit_predict(distance_matrix)
        
        cluster_scores = []
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, label in enumerate(labels) if label == cluster_id]
            
            if len(cluster_indices) > 1:
                cluster_similarities = []
                for i in cluster_indices:
                    for j in cluster_indices:
                        if i != j:
                            cluster_similarities.append(similarity_matrix[i, j])
                
                cluster_scores.append(np.mean(cluster_similarities))
        
        if cluster_scores:
            avg_score = np.mean(cluster_scores)
            if avg_score > best_score:
                best_score = avg_score
                best_n_clusters = n_clusters
                best_labels = labels
    
    pca = PCA(n_components=2, random_state=42)
    pca_result = pca.fit_transform(similarity_matrix)
    
    cluster_info = {}
    for i, label in enumerate(best_labels):
        if label not in cluster_info:
            cluster_info[label] = []
        cluster_info[label].append(similarity_data['structure_names'][i])
    
    logger.info(f"聚类完成: {best_n_clusters} 个聚类，质量评分: {best_score:.3f}")
    
    return {
        'labels': best_labels,
        'cluster_info': cluster_info,
        'pca_result': pca_result,
        'n_clusters': best_n_clusters,
        'score': best_score
    }


def generate_comprehensive_report(
    quality_results: List[Dict],
    similarity_data: Optional[Dict],
    clustering_results: Optional[Dict],
    output_file: Path
) -> None:
    """
    生成综合分析报告
    
    Args:
        quality_results: 质量评估结果
        similarity_data: 相似性分析结果
        clustering_results: 聚类结果
        output_file: 输出文件路径
    """
    from datetime import datetime
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("蛋白质结构批量分析报告\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"工作目录: {output_file.parent}\n\n")
        
        # 质量评估结果
        f.write("1. 结构质量评估\n")
        f.write("-" * 30 + "\n")
        
        status_counts = {}
        for result in quality_results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        f.write(f"总结构数: {len(quality_results)}\n")
        for status, count in status_counts.items():
            percentage = (count / len(quality_results)) * 100
            f.write(f"  {status}: {count} ({percentage:.1f}%)\n")
        
        successful = [r for r in quality_results if r['status'] == 'success']
        if successful:
            residues = [r['num_residues'] for r in successful]
            atoms = [r['num_atoms'] for r in successful]
            
            f.write(f"\n成功结构统计:\n")
            f.write(f"  平均残基数: {np.mean(residues):.1f}\n")
            f.write(f"  残基数范围: {min(residues)} - {max(residues)}\n")
            f.write(f"  平均原子数: {np.mean(atoms):.1f}\n")
            f.write(f"  原子数范围: {min(atoms)} - {max(atoms)}\n")
        
        # 相似性分析结果
        if similarity_data:
            f.write(f"\n2. 结构相似性分析\n")
            f.write("-" * 30 + "\n")
            
            n_structures = len(similarity_data['structure_names'])
            f.write(f"分析结构数: {n_structures}\n")
            
            if 'similarity_results' in similarity_data:
            similarities = [r['similarity_score'] for r in similarity_data['similarity_results'] if r.get('status') == 'success']
            rmsds = [r['rmsd'] for r in similarity_data['similarity_results'] if r.get('rmsd') is not None]
            
            if similarities:
                f.write(f"平均相似性: {np.mean(similarities):.3f}\n")
                f.write(f"相似性范围: {np.min(similarities):.3f} - {np.max(similarities):.3f}\n")
            
            if rmsds:
                f.write(f"平均RMSD: {np.mean(rmsds):.2f} Å\n")
                f.write(f"RMSD范围: {np.min(rmsds):.2f} - {np.max(rmsds):.2f} Å\n")
        
        # 聚类结果
        if clustering_results:
            f.write(f"\n3. 结构聚类分析\n")
            f.write("-" * 30 + "\n")
            
            f.write(f"聚类数: {clustering_results['n_clusters']}\n")
            f.write(f"聚类质量评分: {clustering_results['score']:.3f}\n\n")
            
            cluster_info = clustering_results['cluster_info']
            for cluster_id, members in cluster_info.items():
                f.write(f"聚类 {cluster_id + 1}: {len(members)} 个结构\n")
                for member in members:
                    f.write(f"  - {member}\n")
                f.write("\n")
    
    logger.info(f"报告已生成: {output_file}")
