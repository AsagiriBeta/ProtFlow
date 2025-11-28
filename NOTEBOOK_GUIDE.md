# Notebook文件组织指南

## 📋 概述

本项目的notebook文件已经按照"一个功能一个notebook"的原则重新组织，移除了Colab专用代码，统一使用服务器环境配置。

## 📝 命名规范

采用数字前缀+下划线分隔的功能描述命名：
- `XX_功能模块_具体工具.ipynb`
- 数字前缀表示推荐的执行顺序
- 使用下划线分隔，避免空格
- 功能描述清晰明确

## 🗂️ 文件分类

### 🧬 **核心工作流系列 (00-09)**

| 文件 | 功能 | 描述 |
|------|------|------|
| `00_genome_annotation_to_structure.ipynb` | 基因组注释到结构 | 完整流程：FNA → Prokka注释 → ESM3结构预测 |

### 🔬 **独立工具系列 (10-19)**

| 文件 | 功能 | 描述 |
|------|------|------|
| `10_genome_annotation_prokka.ipynb` | 基因组注释 | 专门的Prokka基因注释工具 |
| `11_protein_structure_esm3.ipynb` | 蛋白质结构预测 | 专门的ESM3结构预测 |
| `12_structure_alignment_dali.ipynb` | 结构比对 | DALI蛋白质结构比对 |
| `13_biosynthetic_cluster_antismash.ipynb` | 抗生素基因簇分析 | antiSMASH生物合成基因簇分析 |

### 📊 **分析工具系列 (20-29)**

| 文件 | 功能 | 描述 |
|------|------|------|
| `20_cds_annotation_comparison.ipynb` | CDS注释比较 | 比较antiSMASH和Prokka的CDS注释差异 |
| `21_batch_structure_analysis.ipynb` | 批量结构分析 | 大规模蛋白质结构分析和聚类 |

### 🎯 **分子对接系列 (01-03)**

ProtFlow原始功能的模块化拆分：

| 文件 | 功能 | 描述 |
|------|------|------|
| `01_protein_structure_prediction.ipynb` | 蛋白质结构预测 | 从序列到结构的预测 |
| `02_pocket_detection_p2rank.ipynb` | 口袋检测 | P2Rank结合口袋检测 |
| `03_ligand_docking_vina.ipynb` | 分子对接 | AutoDock Vina分子对接 |

## 🚀 使用建议

### 📈 **推荐工作流程**

1. **基因组分析流程**: 
   ```
   10_genome_annotation_prokka.ipynb → 11_protein_structure_esm3.ipynb → 12_structure_alignment_dali.ipynb
   ```

2. **完整基因组到结构流程**:
   ```
   00_genome_annotation_to_structure.ipynb (一体化) 
   或
   10_genome_annotation_prokka.ipynb → 11_protein_structure_esm3.ipynb
   ```

3. **分子对接流程**:
   ```
   01_protein_structure_prediction.ipynb → 02_pocket_detection_p2rank.ipynb → 03_ligand_docking_vina.ipynb
   ```

4. **天然产物分析流程**:
   ```
   13_biosynthetic_cluster_antismash.ipynb → 20_cds_annotation_comparison.ipynb
   ```

5. **批量分析流程**:
   ```
   21_batch_structure_analysis.ipynb (用于大规模数据分析)
   ```

### ⚙️ **环境配置**

所有notebook现在都使用统一的服务器环境配置：
- 自动检测JupyterLab/JupyterHub环境
- 使用相对路径和项目根目录
- 统一的依赖检查和安装机制
- 移除所有Google Colab特定代码

### 🔧 **输入输出规范**

每个notebook都有明确的输入输出要求：
- **输入**: 具体文件格式和路径要求
- **输出**: 结果文件位置和格式说明
- **依赖**: 所需的外部工具和Python包

## 🎯 **功能对比**

### **原ProtFlow.ipynb** → **新模块化设计**
- ✅ 结构预测 → `01_protein_structure_prediction.ipynb`
- ✅ 口袋检测 → `02_pocket_detection_p2rank.ipynb`  
- ✅ 分子对接 → `03_ligand_docking_vina.ipynb`
- ✅ 流程整合 → 通过明确的输入输出连接

### **移除的文件**
- ❌ `AntiSMASH_Colab.ipynb` → 替换为 `13_biosynthetic_cluster_antismash.ipynb`
- ❌ `Prokka_ESM3_Workflow_JLab.ipynb` → 与 `Prokka_ESM3_Workflow.ipynb` 合并
- ❌ `ProtFlow.ipynb` → 拆分为三个独立模块

### **保留并重命名的文件**
- ✅ `ESM3_Workflow.ipynb` → `11_protein_structure_esm3.ipynb`
- ✅ `Prokka_Workflow.ipynb` → `10_genome_annotation_prokka.ipynb`
- ✅ `DALI_Protein_Alignment.ipynb` → `12_structure_alignment_dali.ipynb`
- ✅ `Compare_CDS_Annotations.ipynb` → `20_cds_annotation_comparison.ipynb`

## 📁 **结果文件组织**

每个notebook会在工作目录下创建自己的子目录：
```
ProtFlow/
├── structure_prediction_runs/     # 01_结构预测
├── pocket_detection_runs/         # 02_口袋检测  
├── docking_runs/                  # 03_分子对接
├── prokka_runs/                   # 10_Prokka注释
├── esm3_runs/                     # 11_ESM3预测
├── dali_runs/                     # 12_DALI比对
├── antismash_runs/                # 13_antiSMASH
├── cds_comparison_runs/           # 20_CDS比较
└── batch_analysis_runs/           # 21_批量分析
```

## 🔍 **质量保证**

- ✅ 每个notebook只负责一个主要功能
- ✅ 统一的代码风格和文档格式
- ✅ 完善的错误处理和依赖检查
- ✅ 清晰的使用说明和下一步指导
- ✅ 移除Colab依赖，适配服务器环境
- ✅ 模块化的输入输出设计

## 📝 **使用提示**

1. **按数字顺序使用**: 数字前缀表示推荐的执行顺序
2. **检查依赖**: 每个notebook开头都有依赖检查单元格
3. **路径配置**: 在notebook开头配置正确的输入文件路径
4. **结果复用**: 下游notebook可以直接使用上游结果文件
5. **并行使用**: 同一系列的notebook可以独立并行运行

## 🔗 **工具链连接**

notebook之间通过标准文件格式连接：
- 蛋白质序列: `.faa`, `.fa`, `.fasta`
- 结构文件: `.pdb`
- 注释文件: `.gbk`, `.csv`
- 结果汇总: `.csv`, `.txt`
- 可视化: `.png`, `.html`

这样可以确保：
- 结果可复用
- 流程可中断和恢复
- 工具可替换
- 分析可追溯