# ProtFlow

蛋白质结构预测、口袋识别与配体对接的模块化流程。

**📖 [English README](README.md)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)

---

## 🚀 可用工作流

### 1. **ProtFlow** - 结构预测与对接
- **流程**: GenBank → ESM3 → P2Rank → AutoDock Vina
- **笔记本**: [ProtFlow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)
- **用途**: 药物发现、结合位点分析

### 2. **AntiSMASH** - BGC 分析
- **流程**: 基因组 → antiSMASH → BGC 注释
- **笔记本**: [AntiSMASH_Colab.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/AntiSMASH_Colab.ipynb)
- **用途**: 次级代谢物发现

### 3. **Prokka → ESM3 → DALI** ⭐
- **流程**: FNA → Prokka → ESM3 → DALI 格式 PDB
- **笔记本**: 
  - Colab: [Prokka_ESM3_Workflow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/Prokka_ESM3_Workflow.ipynb)
  - JupyterLab: [Prokka_ESM3_Workflow_JLab.ipynb](Prokka_ESM3_Workflow_JLab.ipynb)
- **用途**: 基因组注释、结构蛋白质组学

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

# 或启动 JupyterLab
jupyter lab
```

**Prokka 工作流（JupyterLab）：**
```bash
# ���装 micromamba（如需要）
brew install micromamba  # macOS
# 或: curl -Ls https://micro.mamba.pm/install.sh | bash

# 创建 Prokka 环境
micromamba create -y -n prokka -c bioconda prokka python=3.10
micromamba run -n prokka prokka --setupdb

# 启动笔记本
jupyter lab Prokka_ESM3_Workflow_JLab.ipynb
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

✅ **模块化设计** - 每个步骤都可独立运行  
✅ **高性能** - GPU 加速、缓存、并行处理  
✅ **灵活输入** - GenBank、FASTA、SMILES、分子文件  
✅ **生产就绪** - 结构化日志、错误处理、测试  
✅ **文档完善** - 全面的指南和示例

### 项目结构
```
ProtFlow/
├── esm3_pipeline/          # 核心模块
│   ├── seq_parser.py       # GenBank/FASTA 解析
│   ├── esm3_predict.py     # ESM3 结构预测
│   ├── p2rank.py           # P2Rank 口袋检测
│   ├── ligand_prep.py      # 配体准备（SMILES/文件）
│   ├── vina_dock.py        # AutoDock Vina 对接
│   ├── reporting.py        # PDF 报告生成
│   └── config.py           # 配置管理
├── scripts/
│   ├── runner.py           # 主 CLI 入口
│   ├── check_deps.py       # 依赖检查器
│   └── setup_*.sh          # 系统设置脚本
├── ProtFlow.ipynb          # 主 Colab 笔记本
├── Prokka_ESM3_Workflow*.ipynb  # Prokka 工作流
└── README.md               # 本文件
```

### 核心模块

**`seq_parser`** - 序列解析和过滤
- `extract_proteins_from_gbk()` - 从 GenBank 提取蛋白质
- `filter_and_select()` - 按长度过滤和选择序列

**`esm3_predict`** - 结构预测
- `load_esm3_small()` - 加载 ESM3-sm 模型
- `predict_pdbs()` - 批量预测结构

**`p2rank`** - 口袋检测
- `run_p2rank_batch()` - 在多个 PDB 中检测口袋

**`ligand_prep`** - 配体准备
- `smiles_to_pdbqt()` - 将 SMILES 转换为 PDBQT
- `convert_ligand()` - 转换各种格式

**`vina_dock`** - 分子对接
- `dock_to_pockets()` - 将配体对接到预测的口袋

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


