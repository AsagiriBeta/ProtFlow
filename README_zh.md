# ProtFlow

蛋白质结构预测、口袋识别与配体对接的模块化流程。

**📖 [English README](README.md) | [Complete Documentation](DOCUMENTATION.md) | [完整文档](DOCUMENTATION_zh.md)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)

---

## 概述

ProtFlow 将多个生物信息学工具整合到一个无缝的模块化流程中：

- **GenBank 解析** → 从 GenBank 文件提取蛋白质序列
- **结构预测** → 使用 ESM3-sm 预测3D结构
- **口袋识别** → 使用 P2Rank 识别结合口袋
- **配体对接** → 使用 AutoDock Vina 进行配体对接
- **报告生成** → 创建综合性 PDF 报告

**若需进行 antiSMASH BGC 注释**，请使用独立的 [AntiSMASH_Colab.ipynb](AntiSMASH_Colab.ipynb) 笔记本。

每个步骤都是独立的，可以单独运行或作为完整流程运行。

---

## 系统要求

- **Python 3.12+**（推荐）
- 支持 CUDA 的 GPU（推荐用于结构预测）
- HuggingFace 账户和 token（用于访问 ESM3 模型）

---

## 快速开始

### 方式一：Google Colab（推荐新手）

**无需安装！在浏览器中使用免费 GPU 运行。**

1. **结构预测与对接**：打开 [ProtFlow.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/ProtFlow.ipynb)
2. **antiSMASH 分析**：打开 [AntiSMASH_Colab.ipynb](https://colab.research.google.com/github/AsagiriBeta/ProtFlow/blob/main/AntiSMASH_Colab.ipynb)
3. 启用 GPU：`运行时 → 更改运行时类型 → GPU`（仅 ProtFlow 需要）
4. 按顺序运行单元格
5. 获取 HuggingFace token：[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)（仅 ProtFlow 需要）

适用于：
- 测试流程
- 无本地 GPU
- 快速分析（< 20 个蛋白质）

### 方式二：本地安装

```bash
# 克隆仓库
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# 创建虚拟环境（推荐 Python 3.12+）
python3.12 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -e .

# 安装系统工具（macOS）
bash scripts/setup_macos.sh
# 或 Ubuntu/Debian
bash scripts/setup_ubuntu.sh

# 验证安装
python scripts/check_deps.py
```

### 基本用法

```bash
# 完整流程示例
python -m scripts.runner \
    --parse-gbk \
    --predict \
    --p2rank \
    --vina \
    --report \
    --smiles "CCO" \
    --limit 5
```

### 命令行选项

所有标志都是可选的 - 只运行您需要的步骤：

- `--parse-gbk` - 解析 GenBank 文件以提取蛋白质
- `--predict` - 使用 ESM3-sm 预测结构
- `--p2rank` - 识别结合口袋
- `--vina` - 运行分子对接
- `--report` - 生成 PDF 报告

**常用参数：**
- `--gbk-dir DIR` - GenBank 文件目录（默认：`./esm3_pipeline/gbk_input`）
- `--smiles STR` - 配体的 SMILES 字符串
- `--ligand FILE` - 配体文件（MOL2、SDF、PDB 等）
- `--limit N` - 限制序列数量
- `--config FILE` - 从文件加载配置
- `--parallel` - 启用并行处理
- `--workers N` - 并行工作进程数


### 示例 1：仅结构预测
```bash
python -m scripts.runner --parse-gbk --predict --limit 10
```

### 示例 2：使用 SMILES 对接
```bash
python -m scripts.runner --vina --smiles "CC(=O)O" --parallel --workers 4
```

### 示例 3：使用配置文件
创建 `config.json`：
```json
{
  "max_sequences": 10,
  "enable_cache": true,
  "vina_exhaustiveness": 8
}
```

运行：
```bash
python -m scripts.runner --config config.json --predict --report
```

### 示例 4：编程使用
```python
from pathlib import Path
from esm3_pipeline import seq_parser, esm3_predict

# 解析 GenBank 文件
n = seq_parser.extract_proteins_from_gbk(
    Path("./gbk_input"),
    Path("./proteins.faa")
)

# 预测结构
model, device = esm3_predict.load_esm3_small()
selected = seq_parser.filter_and_select(Path("./proteins.faa"), limit=5)
esm3_predict.predict_pdbs(model, selected, Path("./pdbs"))
```

---

## 可选：antiSMASH

antiSMASH 不包含在 `requirements.txt` 中，需单独安装：

**Bioconda（推荐）：**
```bash
conda create -y -n antismash antismash
conda activate antismash
download-antismash-databases
```

**Docker（适用于 Apple Silicon）：**
```bash
mkdir -p ~/bin
curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
chmod a+x ~/bin/run_antismash
```

**使用：**
```bash
conda activate antismash
python -m scripts.runner --antismash --gbk-dir ./esm3_pipeline/gbk_input
```

---

## 文档

- **[README.md](README.md)** - 英文简要文档
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - 完整英文文档及 API 参考
- **[DOCUMENTATION_zh.md](DOCUMENTATION_zh.md)** - 完整中文文档及 API 参考

---

## 特性

✅ **模块化设计** - 每个步骤都可独立运行  
✅ **高性能** - GPU 加速、缓存、并行处理  
✅ **灵活输入** - GenBank、FASTA、SMILES、分子文件  
✅ **生产就绪** - 结构化日志、错误处理、测试  
✅ **文档完善** - 全面的 API 文档和示例

---

## 故障排除

**常见问题：**
- "未找到 Java" → 安装 Java：`brew install openjdk`（macOS）或 `apt-get install default-jre`（Ubuntu）
- "未找到 OpenBabel" → 安装：`brew install open-babel`（macOS）或 `apt-get install openbabel`（Ubuntu）
- "未找到 Vina" → 安装：`brew install autodock-vina`（macOS）或 `apt-get install autodock-vina`（Ubuntu）
- ESM3 模型失败 → 设置 `HF_TOKEN` 环境变量

**调试模式：**
```bash
python -m scripts.runner --log-level DEBUG --log-file debug.log --predict
```

**检查依赖：**
```bash
python scripts/check_deps.py
```

---

## 许可证

本仓库依赖于具有自己许可证的第三方工具（P2Rank: Apache 2.0、AutoDock Vina: Apache 2.0、OpenBabel: GPL v2、antiSMASH: AGPL v3）。在重新分发之前请查看它们的许可证。

---

## 引用

如果您在研究中使用 ProtFlow，请引用底层工具：
- **ESM**: [Evolutionary Scale Modeling](https://github.com/evolutionaryscale/esm)
- **P2Rank**: Krivák & Hoksza (2018). Journal of Cheminformatics, 10(1), 39.
- **AutoDock Vina**: Trott & Olson (2010). Journal of Computational Chemistry, 31(2), 455-461.
- **antiSMASH**: Blin et al. (2023). Nucleic Acids Research, 51(W1), W46-W50.

---

**详细文档请参阅 [DOCUMENTATION_zh.md](DOCUMENTATION_zh.md)**

