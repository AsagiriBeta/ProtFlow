# ProtFlow

蛋白质结构预测、口袋识别与配体对接的模块化流程。

**📖 [English README](README.md)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/00_genome_annotation_to_structure.ipynb)

---

## 📖 文档导航

### 快速链接
- [🏠 文档中心](docs/index.md) - 完整文档索引
- [⚡ 快速开始](docs/user-guide/quick-start.md) - 5分钟上手ProtFlow
- [🔧 安装指南](docs/user-guide/installation.md) - 详细安装步骤
- [📓 Notebook指南](docs/user-guide/migration/notebook-usage.md) - 如何使用Jupyter笔记本
- [🔄 从Colab迁移](docs/user-guide/migration/from-colab.md) - 从Google Colab迁移到服务器
- [⚙️ 配置参考](docs/configuration/overview.md) - 配置选项和示例

### 用户指南
- [教程：基础使用](docs/user-guide/tutorial/basic-usage.md) - 基础工作流程教程
- [教程：高级功能](docs/user-guide/tutorial/advanced-features.md) - 高级使用模式
- [故障排除指南](docs/user-guide/tutorial/troubleshooting.md) - 常见问题和解决方案

### 开发者资源
- [架构概览](docs/developer-guide/architecture.md) - 系统设计和架构
- [API参考](docs/developer-guide/api-reference.md) - Python API文档
- [贡献指南](docs/developer-guide/contributing.md) - 如何为项目做贡献

### 项目信息
- [项目总结](docs/about/project-summary.md) - 项目概览和成果
- [重构总结](docs/about/refactoring-summary.md) - 代码重构详情
- [文档审计](docs/audit/documentation-audit.md) - 文档质量审查
- [重组报告](docs/audit/reorganization-report.md) - 最近文档更新

---

---

## 🚀 可用工作流

### 📂 Notebook 组织结构
所有笔记本现在都组织在 `/notebooks/` 目录中，采用系统化编号：
- **核心工作流程** (00-09): 完整的分析流程
- **工具** (10-19): 单独的分析工具
- **分析** (20-29): 结果分析和比较工具

### 1. **核心工作流程** - 完整流程

#### 🧬 **Prokka → ESM3 → DALI** (推荐)
- **流程**: FNA → Prokka → ESM3 → DALI-ready PDBs
- **笔记本**: [`notebooks/core/00_genome_annotation_to_structure.ipynb`](notebooks/core/00_genome_annotation_to_structure.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/00_genome_annotation_to_structure.ipynb)
- **用途**: 基因组注释、结构蛋白质组学

#### 🎯 **结构预测与分析**
- **流程**: 蛋白质序列 → ESM3 → 结构分析
- **笔记本**: [`notebooks/core/01_protein_structure_prediction.ipynb`](notebooks/core/01_protein_structure_prediction.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/01_protein_structure_prediction.ipynb)
- **用途**: 蛋白质结构预测和分析

#### 🔍 **口袋检测与分析**
- **流程**: PDB结构 → P2Rank → 口袋分析
- **笔记本**: [`notebooks/core/02_pocket_detection_p2rank.ipynb`](notebooks/core/02_pocket_detection_p2rank.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/02_pocket_detection_p2rank.ipynb)
- **用途**: 结合位点检测和分析

#### ⚗️ **配体对接与分析**
- **流程**: PDB + 配体 → Vina → 对接分析
- **笔记本**: [`notebooks/core/03_ligand_docking_vina.ipynb`](notebooks/core/03_ligand_docking_vina.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/core/03_ligand_docking_vina.ipynb)
- **用途**: 分子对接和结合分析

### 2. **单独工具** - 独立分析

#### 📝 **基因组注释 (Prokka)**
- **工具**: Prokka 基因组注释
- **笔记本**: [`notebooks/tools/10_genome_annotation_prokka.ipynb`](notebooks/tools/10_genome_annotation_prokka.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/10_genome_annotation_prokka.ipynb)
- **用途**: 细菌基因组注释

#### 🧪 **蛋白质结构预测 (ESM3)**
- **工具**: ESM3 结构预测
- **笔记本**: [`notebooks/tools/11_protein_structure_esm3.ipynb`](notebooks/tools/11_protein_structure_esm3.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/11_protein_structure_esm3.ipynb)
- **用途**: 单个蛋白质结构预测

#### 📊 **结构比对 (DALI)**
- **工具**: DALI 结构比对
- **笔记本**: [`notebooks/tools/12_structure_alignment_dali.ipynb`](notebooks/tools/12_structure_alignment_dali.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/12_structure_alignment_dali.ipynb)
- **用途**: 蛋白质结构比较

#### 🧬 **BGC 分析 (antiSMASH)**
- **工具**: antiSMASH BGC 检测
- **笔记本**: [`notebooks/tools/13_biosynthetic_cluster_antismash.ipynb`](notebooks/tools/13_biosynthetic_cluster_antismash.ipynb)
- **Colab**: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/master/notebooks/tools/13_biosynthetic_cluster_antismash.ipynb)
- **用途**: 抗生素合成基因簇分析

### 3. **分析工具** - 结果处理

#### 📈 **CDS 注释比较**
- **工具**: 比较不同注释结果
- **笔记本**: [`notebooks/analysis/20_cds_annotation_comparison.ipynb`](notebooks/analysis/20_cds_annotation_comparison.ipynb)
- **用途**: 注释质量评估

#### 📊 **批量结构分析**
- **工具**: 分析多个结构
- **笔记本**: [`notebooks/analysis/21_batch_structure_analysis.ipynb`](notebooks/analysis/21_batch_structure_analysis.ipynb)
- **用途**: 大规模结构分析

---

## 📦 快速开始

### 方式一：Google Colab（推荐新手）

1. 点击上方工作流链接
2. 启用 GPU：`运行时 → 更改运行时类型 → GPU`
3. 获取 HuggingFace token：[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
4. 按顺序运行单元格

### 方式二：本地 / JupyterLab

```bash
# 克隆仓库
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# 安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 设置 HuggingFace token
export HF_TOKEN=hf_your_token_here

# 运行 CLI
python -m scripts.runner --parse-gbk --predict --limit 5

# 或启动 JupyterLab 与所有笔记本
jupyter lab notebooks/
```

**Prokka 工作流（JupyterLab）：**
```bash
# ���装 micromamba（如需要）
brew install micromamba  # macOS
# 或: curl -Ls https://micro.mamba.pm/install.sh | bash

# 创建 Prokka 环境
micromamba create -y -n prokka -c bioconda prokka python=3.10
micromamba run -n prokka prokka --setupdb

# 启动笔记本导航器
jupyter lab notebooks/
# 然后导航到: notebooks/core/00_genome_annotation_to_structure.ipynb
```

配置选项参见 `.env.example`。

---

## 💡 使用示例

### CLI 流程
```bash
# 完整流程：解析 → 预测 → 对接 → 报告
python -m scripts.runner --parse-gbk --predict --p2rank --vina --report --smiles "CCO" --limit 5

# 仅结构预测
python -m scripts.runner --predict --limit 10

# 使用自定义配体对接
python -m scripts.runner --vina --ligand my_drug.mol2 --parallel

# antiSMASH BGC 分析
python -m scripts.runner --antismash --gbk-dir ./genomes
```

**CLI 选项：**
```bash
# 工作流步骤（可任意组合）
--parse-gbk          # 从 GenBank 文件提取蛋白质
--predict            # 使用 ESM3 预测 3D 结构
--p2rank             # 检测结合口袋
--vina               # 运行分子对接
--report             # 生成 PDF 报告
--antismash          # 运行 antiSMASH BGC 分析

# 输入/输出
--gbk-dir DIR        # GenBank 文件目录（默认: ./esm3_pipeline/gbk_input）
--smiles STR         # 配体 SMILES 字符串
--ligand FILE        # 配体文件（MOL2/SDF/PDB/等）
--limit N            # 最大处理序列数
--config FILE        # 从 JSON/YAML 加载配置

# 性能
--parallel           # 启用并行处理
--workers N          # 并行工作进程数（默认: 4）
--log-level LEVEL    # 日志级别: DEBUG/INFO/WARNING/ERROR
```

### Python API
```python
from pathlib import Path
from esm3_pipeline import seq_parser, esm3_predict, p2rank, vina_dock

# 1. 解析 GenBank 文件
n = seq_parser.extract_proteins_from_gbk(
    Path("./gbk_input"), 
    Path("./proteins.faa")
)

# 2. 过滤和选择序列
selected = seq_parser.filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=5
)

# 3. 预测结构
model, device = esm3_predict.load_esm3_small()
esm3_predict.predict_pdbs(model, selected, Path("./pdbs"))

# 4. 检测口袋
p2rank.run_p2rank_batch(Path("./pdbs"), Path("./pockets"))

# 5. 对接配体
from esm3_pipeline.ligand_prep import smiles_to_pdbqt
ligand = smiles_to_pdbqt("CCO", Path("./ligand.pdbqt"))
vina_dock.dock_to_pockets(
    Path("./pdbs/protein.pdb"),
    ligand,
    Path("./pockets/protein_predictions.csv"),
    Path("./docking")
)
```

### 配置文件
创建 `config.json`：
```json
{
  "max_sequences": 10,
  "min_seq_length": 50,
  "max_seq_length": 1200,
  "enable_cache": true,
  "vina_exhaustiveness": 8,
  "vina_box_size": 20,
  "num_workers": 4,
  "log_level": "INFO"
}
```
运行：`python -m scripts.runner --config config.json --predict --report`

### 环境变量
```bash
export HF_TOKEN=hf_xxxxx              # HuggingFace token（必需）
export PROTFLOW_BASE_DIR=./output     # 基础目录
export PROTFLOW_MAX_SEQUENCES=20      # 最大序列数
export PROTFLOW_LOG_LEVEL=DEBUG       # 日志级别
```

---

## 🔧 可选：antiSMASH

antiSMASH 不包含在 `requirements.txt` 中，需单独安装：

```bash
# Bioconda（推荐）
conda create -y -n antismash antismash
conda activate antismash
download-antismash-databases

# Docker（适用于 Apple Silicon）
mkdir -p ~/bin
curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
chmod a+x ~/bin/run_antismash
```

---

## 📚 特性

✅ **完全重新组织** - 系统化的笔记本编号和组织结构  
✅ **模块化设计** - 每个步骤都可独立运行  
✅ **高性能** - GPU 加速、缓存、并行处理  
✅ **灵活输入** - GenBank、FASTA、SMILES、分子文件  
✅ **生产就绪** - 结构化日志、错误处理、测试  
✅ **全面文档** - 完整的指南、API参考、架构文档  
✅ **多语言支持** - 中英文文档

### 项目结构
```
ProtFlow/
├── notebooks/                    # Jupyter 笔记本（已完全重新组织）
│   ├── core/                    # 核心分析工作流程 (00-09)
│   │   ├── 00_genome_annotation_to_structure.ipynb
│   │   ├── 01_protein_structure_prediction.ipynb
│   │   ├── 02_pocket_detection_p2rank.ipynb
│   │   └── 03_ligand_docking_vina.ipynb
│   ├── tools/                   # 单独分析工具 (10-19)
│   │   ├── 10_genome_annotation_prokka.ipynb
│   │   ├── 11_protein_structure_esm3.ipynb
│   │   ├── 12_structure_alignment_dali.ipynb
│   │   └── 13_biosynthetic_cluster_antismash.ipynb
│   └── analysis/                # 结果分析工具 (20-29)
│       ├── 20_cds_annotation_comparison.ipynb
│       └── 21_batch_structure_analysis.ipynb
├── src/protflow/                # Python 源代码（模块化）
│   ├── core/                    # 核心功能
│   ├── prediction/              # 结构预测
│   ├── docking/                 # 分子对接
│   ├── visualization/           # 可视化工具
│   ├── utils/                   # 工具模块
│   └── data/                    # 数据目录
├── scripts/                     # 命令行脚本
├── config/                      # 配置文件
├── data/                        # 输入数据目录
├── outputs/                     # 输出结果目录
├── docs/                        # 完整文档
│   ├── index.md                 # 文档中心
│   ├── user-guide/              # 用户指南和教程
│   ├── configuration/           # 配置参考
│   ├── tools/                   # 工具文档
│   ├── developer-guide/         # 开发者资源
│   └── audit/                   # 项目审计报告
├── tests/                       # 测试文件
└── README.md                    # 本文件
```

### 核心模块 (`protflow.*`)

**`protflow.core`** - 核心功能和数据管理
- 基因组注释和处理
- 结果聚合和报告生成

**`protflow.prediction`** - 结构预测
- `esm3_predict.py` - 基于ESM3的结构预测
- 批处理能力

**`protflow.docking`** - 分子对接和口袋检测
- `p2rank.py` - 结合位点预测
- `vina_dock.py` - 分子对接
- `ligand_prep.py` - 配体准备

**`protflow.visualization`** - 数据可视化
- 结构可视化
- 分析结果绘图

**`protflow.utils`** - 工具模块
- `config.py` - 配置管理
- `logger.py` - 日志工具
- `seq_parser.py` - 序列解析和过滤

**传统模块 (`esm3_pipeline/`)**
- **`seq_parser`** - 序列解析和过滤
- **`esm3_predict`** - 结构预测
- **`p2rank`** - 口袋检测
- **`ligand_prep`** - 配体准备
- **`vina_dock`** - 分子对接

---

## ⚠️ 故障排除

| 问题 | 解决方案 |
|------|----------|
| "未找到 Java" | `brew install openjdk` (macOS) / `apt install default-jre` (Ubuntu) |
| "未找到 OpenBabel" | `brew install open-babel` / `apt install openbabel` |
| "未找到 Vina" | `brew install autodock-vina` / `apt install autodock-vina` |
| ESM3 模型失败 | 设置 `HF_TOKEN` 环境变量 |
| GPU 内存不足 | 减少 `--limit` 或序列长度 |

**调试模式：**
```bash
python -m scripts.runner --log-level DEBUG --log-file debug.log --predict
```

**检查依赖：**
```bash
python scripts/check_deps.py
```

---

## 📄 许可证

本仓库依赖于具有自己许可证的第三方工具（P2Rank: Apache 2.0、AutoDock Vina: Apache 2.0、OpenBabel: GPL v2、antiSMASH: AGPL v3）。在重新分发之前请查看它们的许可证。

---

## 📖 引用

如果您在研究中使用 ProtFlow，请引用底层工具：
- **ESM**: [Evolutionary Scale Modeling](https://github.com/evolutionaryscale/esm)
- **P2Rank**: Krivák & Hoksza (2018). Journal of Cheminformatics, 10(1), 39.
- **AutoDock Vina**: Trott & Olson (2010). Journal of Computational Chemistry, 31(2), 455-461.
- **antiSMASH**: Blin et al. (2023). Nucleic Acids Research, 51(W1), W46-W50.


