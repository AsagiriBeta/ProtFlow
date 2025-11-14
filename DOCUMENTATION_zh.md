# ProtFlow - 完整文档

**版本:** 0.2.0  
**日期:** 2025年10月28日

蛋白质结构预测、口袋识别与配体对接的模块化流程。

---

## 目录

1. [概述](#概述)
2. [安装](#安装)
3. [快速开始](#快速开始)
4. [配置](#配置)
5. [流程组件](#流程组件)
6. [API参考](#api参考)
7. [高级用法](#高级用法)
8. [故障排除](#故障排除)
9. [贡献](#贡献)
10. [更新日志](#更新日志)

---

## 概述

ProtFlow 是一个综合性工具包，将多个生物信息学工具整合到无缝流程中：

### 主流程（ProtFlow）
- **GenBank 解析**：从 GenBank 文件提取蛋白质序列
- **结构预测**：使用 ESM3-sm 模型预测3D结构
- **口袋识别**：使用 P2Rank 识别结合口袋
- **配体准备**：将 SMILES 或分子文件转换为对接就绪格式
- **分子对接**：使用 AutoDock Vina 进行对接
- **报告生成**：创建综合性 PDF 报告

### 附加工作流
- **AntiSMASH**：BGC 注释流程（[AntiSMASH_Colab.ipynb](AntiSMASH_Colab.ipynb)）
- **Prokka-ESM3-DALI**：基因组注释 → 结构预测 → DALI 格式（[Prokka_ESM3_Workflow.ipynb](Prokka_ESM3_Workflow.ipynb)）

### 主要特性

- **模块化设计**：每个步骤都可独立运行
- **灵活输入**：支持 GenBank 文件、FASTA 序列、SMILES 和各种分子格式
- **高性能**：模型缓存、并行处理和 GPU 加速
- **用户友好**：CLI 接口、配置文件和编程 API
- **文档完善**：全面的 API 文档和示例
- **生产就绪**：结构化日志、错误处理和测试

---

## 安装

### 系统要求

- **Python**: 3.12+（推荐）

- **Python**：3.12+
- **操作系统**：macOS、Linux 或 Windows（使用 WSL）
- **内存**：最低 8 GB RAM（结构预测推荐 16+ GB）
- **GPU**：可选，但推荐用于更快的 ESM3 预测

### 前置依赖

安装系统依赖：

#### macOS
```bash
bash scripts/setup_macos.sh
```

此脚本会安装：
- Java JRE（用于 P2Rank）
- OpenBabel（用于配体准备）
- AutoDock Vina（用于对接）

#### Ubuntu/Debian
```bash
bash scripts/setup_ubuntu.sh
```

### Python 包安装

1. **克隆仓库**：
```bash
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow
```

2. **创建虚拟环境**：
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **安装 Python 依赖**：
```bash
pip install -U pip
pip install -r requirements.txt
```

4. **安装 PyTorch**（平台特定）：

   - **macOS（Apple Silicon）**：
     ```bash
     pip install torch
     ```

   - **Linux（仅 CPU）**：
     ```bash
     pip install torch==2.4.* --index-url https://download.pytorch.org/whl/cpu
     ```

   - **Linux（CUDA 12.1）**：
     ```bash
     pip install torch==2.4.* --index-url https://download.pytorch.org/whl/cu121
     ```

5. **安装 ProtFlow 包**（开发模式）：
```bash
pip install -e .
```

### 验证安装

```bash
python scripts/check_deps.py
```

所有必需依赖项应显示 ✓ 标记。

### Hugging Face Token

访问 ESM3 模型需要 Hugging Face token：

1. 在 [huggingface.co](https://huggingface.co) 创建账户
2. 请求访问 `esm3-sm-open-v1` 模型
3. 在 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 创建 token
4. 设置 token：
   ```bash
   export HF_TOKEN=hf_your_token_here
   # 或使用交互式登录
   huggingface-cli login
   ```

### 可选：antiSMASH 安装

antiSMASH 不包含在 `requirements.txt` 中，需单独安装：

#### 方案 A：Bioconda（推荐用于 Linux 和 Intel Mac）

```bash
conda config --add channels conda-forge
conda config --add channels bioconda
conda create -y -n antismash antismash
conda activate antismash
download-antismash-databases
antismash --prepare-data
antismash --version
```

#### 方案 B：Docker（推荐用于 Apple Silicon）

```bash
mkdir -p ~/bin
curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
chmod a+x ~/bin/run_antismash
# 添加到 PATH
export PATH="$HOME/bin:$PATH"
```

使用 Docker wrapper：
```bash
# 使用绝对路径
run_antismash /绝对路径/输入.gbk /绝对路径/输出目录 --taxon bacteria
```

#### Apple Silicon 特别说明

对于 arm64 Mac，使用 Rosetta x86_64 conda 环境：

```bash
softwareupdate --install-rosetta --agree-to-license
arch -x86_64 zsh -c 'CONDA_SUBDIR=osx-64 conda create -y -n antismash antismash'
conda activate antismash
conda config --env --set subdir osx-64
download-antismash-databases
antismash --prepare-data
```

---

## 快速开始

### 示例 1：基本结构预测

```bash
# 将 .gbk 文件放入 esm3_pipeline/gbk_input/
python -m scripts.runner --parse-gbk --predict --limit 5
```

**输出**：PDB 文件位于 `esm3_pipeline/pdbs/`

### 示例 2：完整流程

```bash
python -m scripts.runner \
    --parse-gbk \
    --predict \
    --p2rank \
    --vina \
    --report \
    --smiles "CCO" \
    --limit 3
```

**输出**：
- PDB 结构位于 `esm3_pipeline/pdbs/`
- 口袋预测位于 `esm3_pipeline/pockets_summary.csv`
- 对接结果位于 `esm3_pipeline/vina_results.csv`
- PDF 报告为 `esm3_pipeline/esm3_results_report.pdf`

### 示例 3：使用配置文件

创建 `my_config.json`：
```json
{
  "max_sequences": 10,
  "min_seq_length": 50,
  "max_seq_length": 1200,
  "enable_cache": true,
  "vina_exhaustiveness": 8,
  "num_workers": 4
}
```

运行：
```bash
python -m scripts.runner --config my_config.json --predict --report
```

### 示例 4：编程使用

```python
from pathlib import Path
from esm3_pipeline.config import ProtFlowConfig
from esm3_pipeline.logger import setup_logging
from esm3_pipeline import seq_parser, esm3_predict

# 设置
logger = setup_logging(level='INFO')
config = ProtFlowConfig()

# 解析 GenBank 文件
n = seq_parser.extract_proteins_from_gbk(
    Path("./esm3_pipeline/gbk_input"),
    Path("./proteins.faa")
)
print(f"提取了 {n} 个蛋白质")

# 过滤序列
selected = seq_parser.filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=5
)

# 预测结构
model, device = esm3_predict.load_esm3_small()
esm3_predict.predict_pdbs(model, selected, Path("./pdbs"))
```

### Prokka-ESM3-DALI 工作流

用于基因组注释和结构预测：

```python
# 在 Google Colab 或 Jupyter 中打开 Prokka_ESM3_Workflow.ipynb
# 1. 上传 FNA 文件（核酸序列）
# 2. 配置参数：
OUTPUT_PREFIX = "my_genome"
KINGDOM = "Bacteria"  # 或 "Archaea", "Viruses"
NUM_STEPS = 8         # ESM3 生成步数
MAX_SEQ_LENGTH = 400  # 最大蛋白质长度

# 3. 运行所有单元格 - 工作流将：
#    - 使用 Prokka 注释基因
#    - 使用 ESM3 预测结构
#    - 准备 DALI 就绪的 PDB 文件
#    - 打包结果供下载
```

**输出**：包含 Prokka 注释、ESM3 结构和 DALI 就绪 PDB 文件的 ZIP 文件。

---

## 配置

### 配置文件格式

ProtFlow 支持 JSON 和 YAML 配置文件。

**示例 `config.json`**：
```json
{
  "base_dir": "./esm3_pipeline",
  "gbk_dir": "./esm3_pipeline/gbk_input",
  "pdb_dir": "./esm3_pipeline/pdbs",
  "esm3_model": "esm3-sm-open-v1",
  "min_seq_length": 50,
  "max_seq_length": 1200,
  "max_sequences": null,
  "enable_cache": true,
  "cache_dir": "./esm3_pipeline/.cache",
  "p2rank_version": "2.5.1",
  "vina_exhaustiveness": 8,
  "vina_box_size": 20,
  "num_workers": 4,
  "log_level": "INFO"
}
```

### 环境变量

可以使用环境变量覆盖配置值：

```bash
export PROTFLOW_BASE_DIR="./my_output"
export PROTFLOW_MAX_SEQUENCES=20
export PROTFLOW_LOG_LEVEL="DEBUG"
export HF_TOKEN="hf_xxxxx"
```

### 命令行选项

```bash
python -m scripts.runner --help
```

**常用选项**：
- `--config FILE`：从文件加载配置
- `--parse-gbk`：解析 GenBank 文件
- `--predict`：运行结构预测
- `--p2rank`：运行口袋识别
- `--vina`：运行分子对接
- `--report`：生成 PDF 报告
- `--antismash`：运行 antiSMASH 分析
- `--gbk-dir DIR`：GenBank 文件目录
- `--smiles STR`：配体的 SMILES 字符串
- `--ligand FILE`：配体文件（MOL2、SDF、PDB 等）
- `--limit N`：限制序列数量
- `--parallel`：启用并行处理
- `--workers N`：并行工作进程数
- `--log-level LEVEL`：日志级别（DEBUG、INFO、WARNING、ERROR）
- `--log-file FILE`：记录到文件

---

## 流程组件

### 1. GenBank 解析

从 GenBank/GBFF 文件提取蛋白质序列。

**模块**：`esm3_pipeline.seq_parser`

**功能**：
- 递归目录搜索
- CDS 翻译提取
- 元数据保留（locus_tag、product、gene）
- 序列去重
- 长度过滤
- 按长度排序

**用法**：
```python
from esm3_pipeline.seq_parser import extract_proteins_from_gbk

count = extract_proteins_from_gbk(
    gbk_dir=Path("./gbk_input"),
    out_fasta=Path("./proteins.faa"),
    recursive=True,
    deduplicate=True
)
```

### 2. 结构预测（ESM3）

使用 ESM3-sm 模型预测3D蛋白质结构。

**模块**：`esm3_pipeline.esm3_predict`

**功能**：
- GPU/MPS/CPU 自动检测
- 模型缓存
- 预测缓存
- 进度跟踪
- 批处理
- 跳过现有文件

**用法**：
```python
from esm3_pipeline.esm3_predict import load_esm3_small, predict_pdbs
from Bio import SeqIO

model, device = load_esm3_small()
sequences = list(SeqIO.parse("proteins.faa", "fasta"))

predict_pdbs(
    model=model,
    seq_records=sequences,
    out_dir=Path("./pdbs"),
    num_steps=8,
    show_progress=True,
    cache_predictions=True
)
```

### 3. 口袋识别（P2Rank）

识别和评分潜在的结合口袋。

**模块**：`esm3_pipeline.p2rank`

**功能**：
- 自动下载 P2Rank
- 多线程执行
- 按分数排序口袋
- 坐标提取
- CSV 输出

**用法**：
```python
from esm3_pipeline.p2rank import ensure_p2rank, run_p2rank_on_pdbs

p2rank_jar = ensure_p2rank(version="2.5.1")
results = run_p2rank_on_pdbs(
    p2rank_jar=p2rank_jar,
    pdb_dir=Path("./pdbs"),
    threads=2,
    top_n_pockets=1
)
```

### 4. 配体准备

将配体转换为 PDBQT 格式用于对接。

**模块**：`esm3_pipeline.ligand_prep`

**功能**：
- SMILES 转 3D 结构
- 支持 MOL2、SDF、MOL、PDB 格式
- pH 依赖质子化
- 使用 OpenBabel 进行 PDBQT 转换
- 自动电荷计算

**用法**：
```python
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt

# 从 SMILES
pdbqt = smiles_or_file_to_pdbqt(
    input_str="CCO",
    output_name="ethanol",
    ph=7.4
)

# 从文件
pdbqt = smiles_or_file_to_pdbqt(
    input_str="ligand.mol2"
)
```

### 5. 分子对接（AutoDock Vina）

进行蛋白质-配体对接。

**模块**：`esm3_pipeline.vina_dock`

**功能**：
- 自动受体 PDBQT 准备
- 并行对接支持
- 多种结合模式
- 可配置搜索空间
- 能量评分

**用法**：
```python
from esm3_pipeline.vina_dock import run_vina
import pandas as pd

pockets_df = pd.read_csv("pockets.csv")

results = run_vina(
    ligand_pdbqt=Path("ligand.pdbqt"),
    pockets=pockets_df,
    box_size=20,
    exhaustiveness=8,
    num_modes=9,
    parallel=True,
    max_workers=4
)
```

### 6. 报告生成

创建综合性 PDF 报告。

**模块**：`esm3_pipeline.reporting`

**功能**：
- 摘要统计
- 结构可视化
- 对接结果表
- 口袋信息
- 可定制布局

**用法**：
```python
from esm3_pipeline.reporting import build_report

build_report(
    base=Path("./"),
    pdb_dir=Path("./pdbs"),
    out_pdf=Path("./report.pdf")
)
```

### 7. antiSMASH 分析（可选）

注释生物合成基因簇。

**模块**：`esm3_pipeline.antismash`

**功能**：
- 自动检测 antiSMASH
- Docker wrapper 支持
- Conda 环境支持
- HTML 报告生成
- 多物种支持

**用法**：
```python
from esm3_pipeline.antismash import run_antismash

result = run_antismash(
    input_path=Path("genome.gbk"),
    out_dir=Path("./antismash_out"),
    extra_args=["--taxon", "bacteria"]
)
```

---

## API参考

### 配置（`esm3_pipeline.config`）

#### `ProtFlowConfig`

中央配置类。

```python
from esm3_pipeline.config import ProtFlowConfig

# 默认配置
config = ProtFlowConfig()

# 从文件加载
config = ProtFlowConfig.from_file("config.json")

# 保存到文件
config.to_file("config.json")

# 访问值
print(config.base_dir)
print(config.esm3_model)
```

**属性**：
- `base_dir`：基础输出目录
- `gbk_dir`：GenBank 文件目录
- `pdb_dir`：PDB 文件目录
- `esm3_model`：ESM3 模型名称
- `min_seq_length`：最小序列长度
- `max_seq_length`：最大序列长度
- `max_sequences`：最大序列数（None = 无限制）
- `enable_cache`：启用缓存
- `cache_dir`：缓存目录
- `p2rank_version`：P2Rank 版本
- `vina_exhaustiveness`：Vina 搜索彻底性
- `vina_box_size`：对接框大小（Å）
- `num_workers`：并行工作进程数
- `log_level`：日志级别

### 序列解析器（`esm3_pipeline.seq_parser`）

#### `extract_proteins_from_gbk()`

从 GenBank 文件提取蛋白质。

```python
from esm3_pipeline.seq_parser import extract_proteins_from_gbk
from pathlib import Path

count = extract_proteins_from_gbk(
    gbk_dir: Path,
    out_fasta: Path,
    recursive: bool = True,
    deduplicate: bool = True
) -> int
```

**参数**：
- `gbk_dir`：包含 .gbk/.gbff 文件的目录
- `out_fasta`：输出 FASTA 文件路径
- `recursive`：搜索子目录
- `deduplicate`：移除重复序列

**返回**：写入的序列数

#### `filter_and_select()`

过滤和选择序列。

```python
from esm3_pipeline.seq_parser import filter_and_select

selected = filter_and_select(
    fasta: Path,
    min_len: int = 50,
    max_len: int = 1200,
    limit: Optional[int] = None,
    out_fasta: Optional[Path] = None,
    sort_by_length: bool = False
) -> List[SeqRecord]
```

**参数**：
- `fasta`：输入 FASTA 文件
- `min_len`：最小序列长度
- `max_len`：最大序列长度
- `limit`：返回的最大序列数
- `out_fasta`：可选输出文件
- `sort_by_length`：按长度排序序列

**返回**：SeqRecord 对象列表

### ESM3 预测（`esm3_pipeline.esm3_predict`）

#### `load_esm3_small()`

加载 ESM3 模型。

```python
from esm3_pipeline.esm3_predict import load_esm3_small

model, device = load_esm3_small(
    device: Optional[str] = None,
    model_name: str = 'esm3-sm-open-v1',
    use_cache: bool = True
) -> Tuple[Any, str]
```

**参数**：
- `device`：使用的设备（'cuda'、'mps'、'cpu' 或 None 自动）
- `model_name`：ESM3 模型名称
- `use_cache`：使用缓存模型（如果可用）

**返回**：(模型, 设备) 元组

#### `predict_pdbs()`

预测蛋白质结构。

```python
from esm3_pipeline.esm3_predict import predict_pdbs

predict_pdbs(
    model: Any,
    seq_records: List[SeqRecord],
    out_dir: Path,
    num_steps: int = 8,
    show_progress: bool = True,
    skip_existing: bool = True,
    cache_predictions: bool = True
) -> None
```

**参数**：
- `model`：加载的 ESM3 模型
- `seq_records`：要预测的序列列表
- `out_dir`：PDB 文件输出目录
- `num_steps`：预测步骤数
- `show_progress`：显示进度条
- `skip_existing`：如果 PDB 已存在则跳过
- `cache_predictions`：缓存预测

### P2Rank（`esm3_pipeline.p2rank`）

#### `ensure_p2rank()`

下载并设置 P2Rank。

```python
from esm3_pipeline.p2rank import ensure_p2rank

p2rank_jar = ensure_p2rank(
    base_dir: Path = Path("."),
    version: str = "2.5.1",
    force_download: bool = False
) -> Path
```

**参数**：
- `base_dir`：下载基础目录
- `version`：P2Rank 版本
- `force_download`：强制重新下载

**返回**：P2Rank JAR 文件路径

#### `run_p2rank_on_pdbs()`

在 PDB 文件上运行 P2Rank。

```python
from esm3_pipeline.p2rank import run_p2rank_on_pdbs

results = run_p2rank_on_pdbs(
    p2rank_jar: Path,
    pdb_dir: Path,
    threads: int = 2,
    visualizations: int = 0,
    top_n_pockets: int = 1
) -> List[Dict[str, Any]]
```

**参数**：
- `p2rank_jar`：P2Rank JAR 路径
- `pdb_dir`：PDB 文件目录
- `threads`：线程数
- `visualizations`：可视化级别（0-3）
- `top_n_pockets`：每个蛋白质返回的顶部口袋数

**返回**：口袋字典列表

### 配体准备（`esm3_pipeline.ligand_prep`）

#### `smiles_or_file_to_pdbqt()`

将配体转换为 PDBQT 格式。

```python
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt

pdbqt_path = smiles_or_file_to_pdbqt(
    input_str: str,
    base_dir: Path = Path("."),
    output_name: str = "ligand",
    ph: float = 7.4
) -> Path
```

**参数**：
- `input_str`：SMILES 字符串或配体文件路径
- `base_dir`：输出基础目录
- `output_name`：输出文件基础名称
- `ph`：质子化的 pH 值

**返回**：PDBQT 文件路径

### Vina 对接（`esm3_pipeline.vina_dock`）

#### `run_vina()`

运行 AutoDock Vina 对接。

```python
from esm3_pipeline.vina_dock import run_vina
import pandas as pd

results_df = run_vina(
    ligand_pdbqt: Path,
    pockets: pd.DataFrame,
    out_base: Path = Path("."),
    box_size: float = 20.0,
    exhaustiveness: int = 8,
    num_modes: int = 9,
    parallel: bool = False,
    max_workers: int = 4
) -> pd.DataFrame
```

**参数**：
- `ligand_pdbqt`：配体 PDBQT 文件路径
- `pockets`：包含口袋信息的 DataFrame
- `out_base`：输出基础目录
- `box_size`：搜索框大小（Å）
- `exhaustiveness`：搜索彻底性
- `num_modes`：结合模式数
- `parallel`：启用并行处理
- `max_workers`：并行工作进程数

**返回**：包含对接结果的 DataFrame

### 日志（`esm3_pipeline.logger`）

#### `setup_logging()`

配置日志系统。

```python
from esm3_pipeline.logger import setup_logging

logger = setup_logging(
    level: str = 'INFO',
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger
```

**参数**：
- `level`：日志级别（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- `log_file`：可选日志文件路径
- `console`：启用控制台输出

**返回**：配置的 logger

#### `get_logger()`

获取模块 logger。

```python
from esm3_pipeline.logger import get_logger

logger = get_logger(__name__)
logger.info("处理已开始")
logger.debug("调试信息")
logger.error("发生错误")
```

### 异常

用于更好错误处理的自定义异常层次结构。

```python
from esm3_pipeline.exceptions import (
    ProtFlowError,           # 基础异常
    ConfigurationError,      # 配置错误
    DependencyError,         # 缺少依赖
    ModelLoadError,          # 模型加载失败
    PredictionError,         # 预测失败
    PocketDetectionError,    # P2Rank 失败
    DockingError,           # Vina 失败
    LigandPreparationError, # 配体准备失败
    ParseError,             # GenBank 解析失败
    AntiSMASHError          # antiSMASH 失败
)
```

---

## 高级用法

### 完整工作流程示例

```python
from pathlib import Path
from esm3_pipeline.config import ProtFlowConfig, set_config
from esm3_pipeline.logger import setup_logging
from esm3_pipeline.seq_parser import extract_proteins_from_gbk, filter_and_select
from esm3_pipeline.esm3_predict import load_esm3_small, predict_pdbs
from esm3_pipeline.p2rank import ensure_p2rank, run_p2rank_on_pdbs
from esm3_pipeline.ligand_prep import smiles_or_file_to_pdbqt
from esm3_pipeline.vina_dock import run_vina
from esm3_pipeline.reporting import build_report
import pandas as pd

# 设置
logger = setup_logging(level='INFO', log_file=Path("pipeline.log"))
config = ProtFlowConfig()
set_config(config)

# 1. 解析 GenBank 文件
logger.info("步骤 1：解析 GenBank 文件")
n = extract_proteins_from_gbk(
    Path("./gbk_input"),
    Path("./proteins.faa")
)
logger.info(f"提取了 {n} 个蛋白质")

# 2. 过滤和选择序列
logger.info("步骤 2：过滤序列")
selected = filter_and_select(
    Path("./proteins.faa"),
    min_len=50,
    max_len=1200,
    limit=10,
    out_fasta=Path("./selected.faa")
)
logger.info(f"选择了 {len(selected)} 个序列")

# 3. 预测结构
logger.info("步骤 3：预测结构")
model, device = load_esm3_small()
predict_pdbs(model, selected, Path("./pdbs"))

# 4. 识别口袋
logger.info("步骤 4：识别口袋")
p2jar = ensure_p2rank(Path("./"))
pockets = run_p2rank_on_pdbs(p2jar, Path("./pdbs"))
pockets_df = pd.DataFrame(pockets)
pockets_df.to_csv("pockets.csv", index=False)
logger.info(f"找到 {len(pockets)} 个口袋")

# 5. 准备配体
logger.info("步骤 5：准备配体")
ligand = smiles_or_file_to_pdbqt("CCO", Path("./"))

# 6. 运行对接
logger.info("步骤 6：运行对接")
results = run_vina(
    ligand, 
    pockets_df, 
    Path("./docking"),
    parallel=True,
    max_workers=4
)
results.to_csv("vina_results.csv", index=False)
logger.info(f"完成 {len(results)} 次对接运行")

# 7. 生成报告
logger.info("步骤 7：生成报告")
build_report(Path("./"), Path("./pdbs"), Path("./report.pdf"))

logger.info("流程完成！")
```

### 并行处理

启用并行处理以加快执行速度：

```bash
# 使用 8 个工作进程进行并行对接
python -m scripts.runner --vina --parallel --workers 8 --smiles "CCO"
```

编程方式：
```python
from esm3_pipeline.vina_dock import run_vina

results = run_vina(
    ligand_pdbqt,
    pockets_df,
    parallel=True,
    max_workers=8
)
```

### 缓存

启用缓存以加速重新运行：

```python
from esm3_pipeline.config import ProtFlowConfig

config = ProtFlowConfig()
config.enable_cache = True
config.cache_dir = Path("./.cache")
```

或通过配置文件：
```json
{
  "enable_cache": true,
  "cache_dir": "./.cache"
}
```

### 自定义工作流

仅运行特定步骤：

```bash
# 仅解析 GenBank 文件
python -m scripts.runner --parse-gbk

# 仅运行口袋识别（需要现有 PDB）
python -m scripts.runner --p2rank

# 仅生成报告
python -m scripts.runner --report
```

---

## 故障排除

### 常见问题

#### 1. "未找到 Java"

**解决方案**：安装 Java JRE
```bash
# macOS
brew install openjdk

# Ubuntu
sudo apt-get install default-jre

# 验证
java -version
```

#### 2. "未找到 OpenBabel"

**解决方案**：安装 OpenBabel
```bash
# macOS
brew install open-babel

# Ubuntu
sudo apt-get install openbabel

# 验证
obabel -V
```

#### 3. "未找到 AutoDock Vina"

**解决方案**：安装 Vina
```bash
# macOS
brew install autodock-vina

# Ubuntu
sudo apt-get install autodock-vina

# 验证
vina --version
```

#### 4. "在 GenBank 文件中未找到序列"

**原因**：
- GenBank 文件为空或损坏
- 没有带翻译的 CDS 特征
- 目录路径错误

**解决方案**：
- 验证 GenBank 文件包含 CDS 特征
- 检查 `--gbk-dir` 路径
- 尝试使用示例 GenBank 文件

#### 5. ESM3 模型加载失败

**原因**：
- 缺少或无效的 HuggingFace token
- 无法访问 esm3-sm-open-v1 模型
- 网络问题

**解决方案**：
```bash
# 设置 token
export HF_TOKEN=hf_xxxxxxxxxxxxx

# 或交互式登录
huggingface-cli login

# 验证访问
python -c "from huggingface_hub import HfApi; HfApi().model_info('esm3-sm-open-v1')"
```

#### 6. 内存不足错误

**原因**：
- 序列太长
- RAM/VRAM 不足

**解决方案**：
- 减少序列长度限制：
  ```bash
  python -m scripts.runner --predict --max-len 800
  ```
- 一次处理更少的序列：
  ```bash
  python -m scripts.runner --predict --limit 5
  ```
- 使用 CPU 而不是 GPU 以获得更小的内存占用

#### 7. P2Rank 静默失败

**原因**：
- 无效的 PDB 文件
- Java 堆空间问题
- 缺少 Java

**解决方案**：
- 验证 PDB 文件有效
- 增加 Java 堆空间：
  ```bash
  export JAVA_OPTS="-Xmx4g"
  ```
- 检查 Java 安装：
  ```bash
  java -version
  ```

#### 8. antiSMASH："未找到命令"

**原因**：
- 未安装 antiSMASH
- 错误的 conda 环境
- 未设置 PATH

**解决方案**：
```bash
# 激活 conda 环境
conda activate antismash

# 验证安装
which antismash
antismash --version

# 如果使用 Docker wrapper
which run_antismash
```

#### 9. 对接产生较差的结果

**可能的改进**：
- 增加彻底性：
  ```bash
  python -m scripts.runner --vina --exhaustiveness 16
  ```
- 增加框大小：
  ```bash
  python -m scripts.runner --vina --box-size 25
  ```
- 使用更多结合模式：
  ```bash
  python -m scripts.runner --vina --num-modes 20
  ```

#### 10. 性能慢

**优化**：
- 启用缓存：
  ```json
  {"enable_cache": true}
  ```
- 使用 GPU 进行结构预测
- 启用并行对接：
  ```bash
  python -m scripts.runner --vina --parallel --workers 8
  ```
- 减少序列数量：
  ```bash
  python -m scripts.runner --predict --limit 10
  ```

### 调试模式

启用详细日志记录：

```bash
python -m scripts.runner --log-level DEBUG --log-file debug.log --predict
```

检查日志文件以获取正在发生的详细信息。

### 获取帮助

1. **检查文档**：README.md、API.md、本文件
2. **运行依赖检查**：`python scripts/check_deps.py`
3. **启用调试日志**：`--log-level DEBUG`
4. **检查问题跟踪器**：[GitHub Issues](https://github.com/AsagiriBeta/ProtFlow/issues)
5. **寻求帮助**：开启新 issue 并提供：
   - 您的操作系统和 Python 版本
   - 完整的命令或脚本
   - 完整的错误消息
   - `python scripts/check_deps.py` 的输出

---

## 贡献

我们欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细指南。

### 贡献者快速入门

1. **Fork 并克隆**：
```bash
git clone https://github.com/YOUR_USERNAME/ProtFlow.git
cd ProtFlow
```

2. **创建虚拟环境**：
```bash
python -m venv venv
source venv/bin/activate
```

3. **以开发模式安装**：
```bash
pip install -e ".[dev]"
```

4. **创建分支**：
```bash
git checkout -b feature/your-feature-name
```

5. **进行更改并测试**：
```bash
pytest tests/
```

6. **检查代码质量**：
```bash
black esm3_pipeline scripts
isort esm3_pipeline scripts
flake8 esm3_pipeline scripts
mypy esm3_pipeline
```

7. **提交并推送**：
```bash
git add .
git commit -m "添加功能：描述"
git push origin feature/your-feature-name
```

8. **在 GitHub 上创建 Pull Request**

### 代码风格

- 遵循 PEP 8
- 使用类型提示
- 编写全面的文档字符串
- 为新功能添加测试
- 保持函数专注和模块化

### 测试

```bash
# 运行所有测试
pytest tests/

# 带覆盖率运行
pytest --cov=esm3_pipeline tests/

# 运行特定测试
pytest tests/test_pipeline.py::test_function_name
```

---

## 更新日志

### [0.2.0] - 2025-10-28

#### 新增
- **配置管理**：带 JSON/YAML 支持的集中配置系统
- **日志系统**：带彩色控制台输出和文件日志的结构化日志
- **错误处理**：用于更好错误消息的自定义异常层次结构
- **测试**：带 CI/CD 集成的综合测试套件
- **性能**：模型缓存、并行对接、预测缓存
- **功能**：序列去重、输入验证、多口袋支持
- **开发工具**：setup.py、.gitignore、GitHub Actions、代码质量工具

#### 更改
- **重构模块**：所有模块均增强了类型提示和文档字符串
- **改进的 CLI**：更好的参数处理和验证
- **增强的文档**：综合性 API 文档和示例

#### 修复
- GenBank 解析边缘情况
- 模型加载中的内存泄漏
- 并行对接中的竞态条件
- Windows 上的路径处理

### [0.1.0] - 2025-10-15

- 初始版本
- 基本流程功能
- Jupyter notebook 界面

---

## 许可证

本仓库包含一个依赖于具有自己许可证的第三方工具的工作流程：
- **P2Rank**：Apache License 2.0
- **AutoDock Vina**：Apache License 2.0
- **OpenBabel**：GPL v2
- **ESM3**：模型特定许可证（检查 HuggingFace）
- **antiSMASH**：AGPL v3

在重新分发之前请查看它们的许可证。

---

## 引用

如果您在研究中使用 ProtFlow，请引用：

```bibtex
@software{protflow2025,
  title={ProtFlow: 用于蛋白质结构预测和分析的模块化流程},
  author={Your Name},
  year={2025},
  url={https://github.com/AsagiriBeta/ProtFlow}
}
```

并引用底层工具：
- **ESM**：[Evolutionary Scale Modeling](https://github.com/evolutionaryscale/esm)
- **P2Rank**：Krivák, R., & Hoksza, D. (2018). P2Rank: machine learning based tool for rapid and accurate prediction of ligand binding sites from protein structure. Journal of cheminformatics, 10(1), 39.
- **AutoDock Vina**：Trott, O., & Olson, A. J. (2010). AutoDock Vina: improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of computational chemistry, 31(2), 455-461.
- **antiSMASH**：Blin, K., et al. (2023). antiSMASH 7.0: new and improved predictions for detection, regulation, chemical structures and visualisation. Nucleic acids research, 51(W1), W46-W50.

---

**了解更多信息，请访问 [GitHub 仓库](https://github.com/AsagiriBeta/ProtFlow)。**

