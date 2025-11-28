# ProtFlow Notebook 索引指南

本文档详细介绍了ProtFlow项目中所有Jupyter Notebook的组织结构和使用方法。

## 📚 Notebook 组织结构

所有Notebook都按照功能进行了系统化的重新组织，采用编号系统便于查找和使用。

### 🧬 核心工作流程 (00-09)

这些Notebook提供了完整的分析工作流程，从输入数据到最终结果。

#### `notebooks/core/00_genome_annotation_to_structure.ipynb`
**Prokka → ESM3 → DALI 完整工作流程**
- **功能**: 基因组注释到蛋白质结构的完整pipeline
- **输入**: FNA核酸序列文件
- **处理**: Prokka注释 → ESM3结构预测 → DALI格式准备
- **输出**: 带注释的蛋白质序列和DALI-ready的PDB文件
- **使用场景**: 基因组学研究中快速获得结构信息
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/core/00_genome_annotation_to_structure.ipynb)

#### `notebooks/core/01_protein_structure_prediction.ipynb`
**蛋白质结构预测工作流程**
- **功能**: 专门用于蛋白质三维结构预测
- **输入**: 蛋白质序列（FASTA格式）
- **处理**: ESM3模型预测 → 结构质量评估 → 结果可视化
- **输出**: PDB结构文件和置信度评分
- **使用场景**: 单个或批量蛋白质结构预测
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/core/01_protein_structure_prediction.ipynb)

#### `notebooks/core/02_pocket_detection_p2rank.ipynb`
**结合口袋检测工作流程**
- **功能**: 蛋白质结合口袋的自动检测和分析
- **输入**: PDB蛋白质结构文件
- **处理**: P2Rank算法检测 → 口袋排序 → 特征分析
- **输出**: 口袋坐标、评分和可视化结果
- **使用场景**: 药物靶点识别和结合位点分析
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/core/02_pocket_detection_p2rank.ipynb)

#### `notebooks/core/03_ligand_docking_vina.ipynb`
**分子对接工作流程**
- **功能**: 蛋白质-配体分子对接分析
- **输入**: 蛋白质结构 + 配体分子
- **处理**: AutoDock Vina对接 → 结合亲和力计算 → 构象优化
- **输出**: 对接构象和结合评分
- **使用场景**: 药物筛选和结合机制研究
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/core/03_ligand_docking_vina.ipynb)

### 🛠️ 独立分析工具 (10-19)

这些Notebook提供独立的分析功能，可以单独使用或组合到自定义工作流程中。

#### `notebooks/tools/10_genome_annotation_prokka.ipynb`
**基因组注释工具 (Prokka)**
- **功能**: 细菌基因组的专业注释
- **输入**: 细菌基因组序列（FNA/FASTA）
- **处理**: Prokka注释 → 基因预测 → 功能注释
- **输出**: 注释后的GenBank文件和蛋白质序列
- **使用场景**: 新测序基因组的初步分析
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/tools/10_genome_annotation_prokka.ipynb)

#### `notebooks/tools/11_protein_structure_esm3.ipynb`
**蛋白质结构预测工具 (ESM3)**
- **功能**: 基于ESM3的蛋白质结构预测
- **输入**: 蛋白质氨基酸序列
- **处理**: ESM3模型推理 → 结构生成 → 质量评估
- **输出**: PDB格式结构文件
- **使用场景**: 单个蛋白质的结构预测
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/tools/11_protein_structure_esm3.ipynb)

#### `notebooks/tools/12_structure_alignment_dali.ipynb`
**结构比对工具 (DALI)**
- **功能**: 蛋白质结构相似性比较
- **输入**: 多个PDB结构文件
- **处理**: DALI算法比对 → 相似性评分 → 结构叠加
- **输出**: 比对结果和相似性矩阵
- **使用场景**: 结构家族分析和进化研究
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/tools/12_structure_alignment_dali.ipynb)

#### `notebooks/tools/13_biosynthetic_cluster_antismash.ipynb`
**抗生素合成基因簇分析工具 (antiSMASH)**
- **功能**: 生物合成基因簇的识别和分析
- **输入**: 细菌或真菌基因组（GenBank/FASTA）
- **处理**: antiSMASH检测 → BGC分类 → 产物预测
- **输出**: BGC注释报告和基因簇序列
- **使用场景**: 天然产物发现和抗生素研究
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/tools/13_biosynthetic_cluster_antismash.ipynb)

### 📊 结果分析工具 (20-29)

这些Notebook用于分析和比较不同分析流程的结果。

#### `notebooks/analysis/20_cds_annotation_comparison.ipynb`
**CDS注释比较工具**
- **功能**: 比较不同注释工具的结果
- **输入**: 多个注释结果文件
- **处理**: 注释一致性分析 → 差异识别 → 质量评估
- **输出**: 比较报告和一致性统计
- **使用场景**: 注释质量评估和工具比较
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/analysis/20_cds_annotation_comparison.ipynb)

#### `notebooks/analysis/21_batch_structure_analysis.ipynb`
**批量结构分析工具**
- **功能**: 大规模蛋白质结构的统计分析
- **输入**: 多个PDB结构文件
- **处理**: 结构特征提取 → 统计分析 → 聚类分析
- **输出**: 分析报告和可视化图表
- **使用场景**: 结构组学研究和质量评估
- **Colab链接**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/notebooks/analysis/21_batch_structure_analysis.ipynb)

## 🎯 使用建议

### 新用户推荐路径

1. **入门体验**：从 `00_genome_annotation_to_structure.ipynb` 开始
2. **专项学习**：根据兴趣选择对应的工具Notebook
3. **批量处理**：使用分析工具处理大量结果

### 有经验的用户

1. **快速工具**：直接使用对应的工具Notebook
2. **自定义流程**：组合多个工具创建自定义分析流程
3. **结果分析**：使用分析工具深入挖掘结果

### 开发者

1. **理解架构**：先查看核心工作流程的实现
2. **工具集成**：学习独立工具的接口设计
3. **结果处理**：了解分析工具的数据处理方法

## 🔧 技术特点

### 编号系统优势
- **快速定位**：通过编号快速找到需要的功能
- **逻辑分组**：按功能相似性分组，便于理解
- **扩展性**：预留编号空间，便于添加新功能

### 统一设计
- **界面一致**：所有Notebook采用统一的界面设计
- **输入规范**：标准化的输入格式和要求
- **输出格式**：一致的输出结构和命名规范

### 互操作性
- **模块化**：可以独立运行，也可以组合使用
- **数据兼容**：输出格式兼容，可以作为下一个工具的输入
- **流程衔接**：支持构建复杂的分析流程

## 📋 最佳实践

### 运行前准备
1. **检查系统要求**：确保有足够的磁盘空间和内存
2. **准备输入数据**：按照每个Notebook的要求准备数据
3. **设置环境变量**：特别是 `HF_TOKEN` 等必要的环境变量

### 运行中监控
1. **注意运行时间**：某些分析可能需要较长时间
2. **监控资源使用**：特别是GPU内存使用情况
3. **保存中间结果**：重要的中间结果及时保存

### 运行后处理
1. **验证输出结果**：检查输出文件的完整性和正确性
2. **备份重要结果**：将重要结果备份到安全位置
3. **清理临时文件**：及时清理不再需要的临时文件

## 🆘 故障排除

### 常见问题
- **内存不足**：减少批处理大小或序列数量
- **依赖缺失**：按照故障排除指南安装缺失的软件
- **权限问题**：确保有足够的文件系统权限

### 获取帮助
- 查看具体的Notebook中的故障排除部分
- 参考[故障排除指南](tutorial/troubleshooting.md)
- 在GitHub上提交Issue

---

**💡 提示**：建议按照编号顺序逐步学习核心工作流程，然后根据需要选择专门的工具Notebook。所有Notebook都经过完全重构，与旧版本有很大不同，建议重新查看使用说明。