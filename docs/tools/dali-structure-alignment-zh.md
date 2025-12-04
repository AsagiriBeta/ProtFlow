# DALI 结构比对

DALI (Distance-matrix ALIgnment，距离矩阵比对) 是一个强大的蛋白质结构比较和比对工具。ProtFlow 现在全面支持**在线 DALI 服务器**和**本地 DALI 安装**两种模式。

## 概述

`protflow.prediction.dali` 模块提供：
- ✨ **在线 DALI 服务器**支持 (ekhidna2.biocenter.helsinki.fi)
- 🔄 从在线到本地模式的**自动回退**
- 📦 多结构**批量处理**
- 📊 **结果解析**和 CSV 导出
- 🎯 **易用的 Python API**

## 快速开始

### 基础使用

```python
from pathlib import Path
from protflow.prediction.dali import DaliAligner

# 初始化 aligner（自动模式 - 优先尝试在线）
aligner = DaliAligner(mode='auto', output_dir=Path('./outputs/dali'))

# 比对单个结构
results = aligner.align(
    query_structure=Path('protein.pdb'),
    database='pdb25',
)

# 打印前几个结果
for result in results[:10]:
    print(f"{result.rank}. {result.target_pdb} Z-分数: {result.z_score:.2f}")
```

### 批量处理

```python
from pathlib import Path
from protflow.prediction.dali import batch_align

# 处理目录中的所有 PDB 文件
results_list = batch_align(
    structures_dir=Path('./data/structures'),
    pattern='*.pdb',
    mode='auto',
)

# results_list 是 (query_name, results) 元组的列表
for query_name, results in results_list:
    print(f"{query_name}: 找到 {len(results)} 个比对结果")
```

## 工作模式

### 在线模式

使用赫尔辛基生物中心的 DALI 网络服务器。

**优势：**
- 无需本地安装
- 始终使用最新的 PDB 数据库
- 不需要磁盘空间存储数据库
- 适合偶尔使用

**要求：**
- 互联网连接
- 可访问 ekhidna2.biocenter.helsinki.fi

```python
aligner = DaliAligner(mode='online')
results = aligner.align(Path('protein.pdb'), database='pdb25')
```

**可用数据库：**
- `pdb25` - 25% 序列同一性非冗余集（推荐）
- `pdb50` - 50% 序列同一性非冗余集
- `pdb90` - 90% 序列同一性非冗余集
- `pdb100` - 完整 PDB

### 本地模式

使用本地安装的 DALI (dali.pl)。

**优势：**
- 不需要互联网
- 批量处理更快
- 完全控制数据库版本
- 可使用自定义数据库

**要求：**
- 本地安装 DALI
- 下载 PDB 数据库（≥50 GB）

```python
aligner = DaliAligner(
    mode='local',
    dali_cmd=Path('/usr/local/bin/dali.pl'),
)
results = aligner.align(Path('protein.pdb'))
```

### 自动模式（推荐）

自动选择最佳可用模式。

**行为：**
1. 检查在线 DALI 服务器是否可访问
2. 如果可用，使用在线模式
3. 如果不可用，回退到本地 DALI
4. 如果都不可用，抛出错误

```python
aligner = DaliAligner(mode='auto')  # 默认
```

## Notebook 使用

更新后的 DALI notebook (`notebooks/tools/12_structure_alignment_dali.ipynb`) 提供完整工作流：

1. **配置模式**：选择在线、本地或自动
2. **同步 ESM3 预测**：自动导入预测的结构
3. **批量比对**：一次处理所有结构
4. **结果可视化**：查看和导出结果

### 配置

```python
# 在 notebook 中
DALI_MODE = 'auto'        # 'online', 'local', 或 'auto'
DALI_DATABASE = 'pdb25'   # 在线模式使用
DALI_CMD = None           # dali.pl 路径（None = 自动检测）
```

## API 参考

### DaliAligner 类

```python
class DaliAligner:
    def __init__(
        self,
        mode: str = 'auto',
        dali_cmd: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        timeout: int = 300,
        max_retries: int = 3,
    )
```

**参数：**
- `mode`: 操作模式（'online'、'local' 或 'auto'）
- `dali_cmd`: 本地模式的 dali.pl 路径
- `output_dir`: 输出文件目录
- `timeout`: 在线查询超时时间（秒）
- `max_retries`: 失败请求的最大重试次数

**方法：**

#### align()

```python
def align(
    self,
    query_structure: Path,
    database: str = "pdb25",
    output_name: Optional[str] = None,
) -> List[DaliResult]
```

将单个结构与数据库进行比对。

#### align_batch()

```python
def align_batch(
    self,
    query_structures: Iterable[Path],
    database: str = "pdb25",
    parallel: bool = False,
) -> List[Tuple[str, List[DaliResult]]]
```

批量比对多个结构。

#### summarize_results()

```python
def summarize_results(
    self,
    results_list: List[Tuple[str, List[DaliResult]]],
    top_n: int = 10,
) -> Optional[pd.DataFrame]
```

从批量结果创建汇总 DataFrame。

### DaliResult 类

```python
@dataclass
class DaliResult:
    query_name: str          # 查询名称
    target_pdb: str          # 目标 PDB ID
    rank: int                # 排名
    z_score: float           # Z-分数
    rmsd: float              # RMSD
    lali: Optional[int] = None      # 比对长度
    nres: Optional[int] = None      # 残基数
    identity: Optional[float] = None  # 序列同一性 %
```

### 便捷函数

#### run_dali_alignment()

```python
def run_dali_alignment(
    query_structure: Path,
    mode: str = 'auto',
    database: str = 'pdb25',
    output_dir: Optional[Path] = None,
) -> List[DaliResult]
```

运行 DALI 比对的单行调用。

#### batch_align()

```python
def batch_align(
    structures_dir: Path,
    pattern: str = "*.pdb",
    mode: str = 'auto',
    output_dir: Optional[Path] = None,
) -> List[Tuple[str, List[DaliResult]]]
```

批量处理的单行调用。

## 输出文件

结果保存在输出目录中：

```
outputs/dali/
├── protein1_results.csv          # 单个结果文件
├── protein2_results.csv
├── dali_batch_summary.csv        # 批量汇总
└── protein1/                     # 本地模式创建子目录
    └── dali.log
```

### CSV 格式

```csv
query,target_pdb,rank,z_score,rmsd,lali,nres,identity
protein1,1ABC,1,45.2,1.8,234,250,25.0
protein1,2DEF,2,42.1,2.1,228,250,23.5
```

## 与工作流集成

### ESM3 → DALI 流程

```python
from pathlib import Path
from protflow.prediction import esm3_predict, dali

# 1. 使用 ESM3 预测结构
predictor = esm3_predict.ESM3Predictor()
predictor.predict_batch(sequences, output_dir=Path('./predictions'))

# 2. 使用 DALI 比对预测的结构
aligner = dali.DaliAligner(mode='auto')
results = aligner.align_batch(
    Path('./predictions').glob('*.pdb')
)

# 3. 查找相似结构
summary = aligner.summarize_results(results, top_n=5)
print(summary[summary['z_score'] > 10])  # 高置信度匹配
```

### CLI 集成

```python
# 在你的脚本中
import argparse
from protflow.prediction.dali import run_dali_alignment

parser = argparse.ArgumentParser()
parser.add_argument('structure', type=Path)
parser.add_argument('--mode', default='auto')
args = parser.parse_args()

results = run_dali_alignment(args.structure, mode=args.mode)
for r in results[:10]:
    print(f"{r.target_pdb}: Z={r.z_score:.2f}")
```

## 理解结果

### Z-分数

Z-分数衡量结构相似性的统计显著性：

- **Z > 20**：高度显著，可能同源
- **Z > 10**：显著相似
- **Z > 5**：可能相似
- **Z < 2**：不显著（随机相似性）

### RMSD

均方根偏差衡量结构差异：
- **越低越好**（结构越相似）
- 典型范围：相似蛋白质为 1-5 Å
- > 10 Å 表示结构非常不同

### 结果解读示例

```python
result = results[0]
if result.z_score > 20:
    print(f"与 {result.target_pdb} 强匹配")
    print(f"RMSD: {result.rmsd:.2f} Å")
    print(f"比对长度: {result.lali} 残基")
    print(f"序列同一性: {result.identity:.1f}%")
```

## 故障排除

### 在线模式问题

**问题**："在线 DALI 服务器不可用"

**解决方案：**
1. 检查互联网连接
2. 验证服务器可访问：`curl http://ekhidna2.biocenter.helsinki.fi/dali/`
3. 使用本地模式作为回退
4. 设置 `mode='auto'` 实现自动回退

### 本地模式问题

**问题**："本地 DALI 不可用"

**解决方案：**
1. 安装 DALI：从 [DALI 网站](http://ekhidna.biocenter.helsinki.fi/dali/)下载
2. 显式设置 DALI_CMD：
   ```python
   aligner = DaliAligner(mode='local', dali_cmd=Path('/path/to/dali.pl'))
   ```
3. 将 dali.pl 添加到 PATH
4. 下载 PDB 数据库

### 超时问题

**问题**："DALI 任务未在超时时间内完成"

**解决方案：**
```python
aligner = DaliAligner(
    mode='online',
    timeout=600,  # 增加到 10 分钟
)
```

## 性能提示

### 批量处理

1. **使用本地模式**处理多个结构（>10 个）
2. **增加超时时间**处理大结构
3. **按 Z-分数过滤**减少输出大小
4. **分块处理**数百个结构

```python
# 分块处理
from itertools import islice

def chunked(iterable, n):
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk

for chunk in chunked(all_structures, 10):
    results = aligner.align_batch(chunk)
    # 处理结果...
```

### 在线模式

1. 使用 `pdb25` 加快查询（较小数据库）
2. 设置合理超时（300-600 秒）
3. 启用重试：`max_retries=3`

### 本地模式

1. 使用 SSD 存储数据库
2. 确保足够内存（≥8 GB）
3. 大数据集批处理可在夜间运行

## 高级用法

### 自定义结果过滤

```python
# 按 Z-分数和 RMSD 过滤
high_quality = [
    r for r in results
    if r.z_score > 15 and r.rmsd < 3.0
]

# 按 Z-分数范围分组
import pandas as pd
df = pd.DataFrame([r.to_dict() for r in results])
df['score_range'] = pd.cut(df['z_score'], bins=[0, 5, 10, 20, 100])
print(df.groupby('score_range').size())
```

### 与结构可视化集成

```python
import py3Dmol

# 可视化最佳匹配
top_hit = results[0]
viewer = py3Dmol.view(width=800, height=600)
viewer.addModel(open(f'{top_hit.target_pdb}.pdb').read(), 'pdb')
viewer.setStyle({'cartoon': {'color': 'spectrum'}})
viewer.show()
```

## 参考文献

- **DALI 服务器**：http://ekhidna2.biocenter.helsinki.fi/dali/
- **DALI 论文**：Holm, L. (2020). DALI and the persistence of protein shape. *Protein Science*, 29(1), 128-140.
- **PDB**：https://www.rcsb.org/

## 另见

- [ESM3 结构预测](./esm3-prediction.md)
- [结构分析](../user-guide/tutorial/advanced-features.md)
- [完整工作流](../user-guide/notebook-index.md)
