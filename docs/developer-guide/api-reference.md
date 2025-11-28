# ProtFlow API 参考文档

本文档提供了ProtFlow的完整Python API参考，包括所有公共类、函数和方法。

## 📚 核心模块 API

### protflow.core.config

配置管理模块，提供统一的配置接口。

#### ProtFlowConfig

```python
@dataclass
class ProtFlowConfig:
    """ProtFlow主配置类"""
    
    # 基础配置
    base_dir: Path = Path("./outputs")
    max_sequences: int = 10
    min_seq_length: int = 50
    max_seq_length: int = 1200
    enable_cache: bool = True
    log_level: str = "INFO"
    
    # 工具路径配置
    p2rank_path: Optional[Path] = None
    vina_path: Optional[Path] = None
    java_path: Optional[Path] = None
    
    # 性能配置
    max_workers: int = 4
    batch_size: int = 1
    
    # ESM3配置
    esm3_model_name: str = "esm3-small"
    esm3_device: str = "auto"  # auto, cpu, cuda
    
    # 对接配置
    vina_exhaustiveness: int = 8
    vina_box_size: float = 20.0
    
    # 报告配置
    enable_reporting: bool = True
    report_format: str = "pdf"  # pdf, html, markdown
```

#### 配置加载函数

```python
def load_config(config_file: Optional[Path] = None) -> ProtFlowConfig:
    """从配置文件加载配置
    
    Args:
        config_file: 配置文件路径（JSON或YAML格式）
        
    Returns:
        ProtFlowConfig: 配置对象
        
    Raises:
        ConfigurationError: 配置文件格式错误或选项无效
        FileNotFoundError: 配置文件不存在
        
    Example:
        >>> config = load_config(Path("config.json"))
        >>> print(config.max_sequences)
        10
    """

def load_config_from_env() -> ProtFlowConfig:
    """从环境变量加载配置
    
    支持的环境变量:
    - PROTFLOW_BASE_DIR: 基础输出目录
    - PROTFLOW_MAX_SEQUENCES: 最大序列数量
    - PROTFLOW_LOG_LEVEL: 日志级别
    - PROTFLOW_MAX_WORKERS: 最大工作进程数
    - HF_TOKEN: HuggingFace API令牌（必需）
    
    Returns:
        ProtFlowConfig: 从环境变量创建的配置对象
    """

def merge_configs(base_config: ProtFlowConfig, 
                 override_config: ProtFlowConfig) -> ProtFlowConfig:
    """合并两个配置对象
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
        
    Returns:
        ProtFlowConfig: 合并后的配置对象
    """
```

### protflow.core.logger

结构化日志模块，提供统一的日志接口。

```python
def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        
    Returns:
        logging.Logger: 配置好的日志记录器
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting prediction pipeline")
    """

class StructuredLogger:
    """结构化日志记录器，支持JSON格式输出"""
    
    def __init__(self, name: str, log_file: Optional[Path] = None):
        """初始化结构化日志记录器
        
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径（可选）
        """
    
    def log_event(self, event_type: str, data: Dict[str, Any], 
                  level: str = "INFO") -> None:
        """记录结构化事件
        
        Args:
            event_type: 事件类型
            data: 事件数据字典
            level: 日志级别
            
        Example:
            >>> logger.log_event("prediction_started", {
            ...     "sequence_id": "protein_001",
            ...     "sequence_length": 250,
            ...     "model": "esm3-small"
            ... })
        """
```

### protflow.core.exceptions

自定义异常类，提供详细的错误信息。

```python
class ProtFlowException(Exception):
    """ProtFlow基础异常类"""
    pass

class ConfigurationError(ProtFlowException):
    """配置相关错误"""
    pass

class ValidationError(ProtFlowException):
    """输入验证错误"""
    pass

class ModelLoadError(ProtFlowException):
    """模型加载错误"""
    pass

class PredictionError(ProtFlowException):
    """预测执行错误"""
    pass

class ToolExecutionError(ProtFlowException):
    """外部工具执行错误"""
    pass

class FileNotFoundError(ProtFlowException):
    """文件未找到错误"""
    pass
```

## 🧬 序列处理 API

### protflow.utils.seq_parser

序列解析和处理工具。

```python
class ProteinSequence:
    """蛋白质序列数据类"""
    
    def __init__(self, sequence_id: str, sequence: str, 
                 description: str = "", source_file: Optional[Path] = None):
        """初始化蛋白质序列
        
        Args:
            sequence_id: 序列唯一标识符
            sequence: 氨基酸序列
            description: 序列描述
            source_file: 源文件路径
        """
    
    @property
    def length(self) -> int:
        """序列长度"""
    
    def validate(self) -> bool:
        """验证序列有效性"""

class SequenceParser:
    """序列文件解析器"""
    
    def __init__(self, config: ProtFlowConfig):
        """初始化解析器
        
        Args:
            config: ProtFlow配置对象
        """
    
    def parse_genbank(self, file_path: Path) -> List[ProteinSequence]:
        """解析GenBank文件
        
        Args:
            file_path: GenBank文件路径
            
        Returns:
            List[ProteinSequence]: 解析得到的蛋白质序列列表
            
        Raises:
            FileNotFoundError: 文件不存在
            ValidationError: 文件格式无效
        """
    
    def parse_fasta(self, file_path: Path) -> List[ProteinSequence]:
        """解析FASTA文件
        
        Args:
            file_path: FASTA文件路径
            
        Returns:
            List[ProteinSequence]: 解析得到的蛋白质序列列表
        """
    
    def extract_proteins_from_gbk(self, gbk_dir: Path, 
                                 output_file: Path) -> int:
        """从GenBank文件目录提取蛋白质序列
        
        Args:
            gbk_dir: GenBank文件目录
            output_file: 输出FASTA文件路径
            
        Returns:
            int: 提取的蛋白质序列数量
            
        Example:
            >>> parser = SequenceParser(config)
            >>> count = parser.extract_proteins_from_gbk(
            ...     Path("gbk_input"), Path("proteins.faa"))
            >>> print(f"提取了 {count} 个蛋白质序列")
        """

def filter_and_select_sequences(sequences: List[ProteinSequence],
                               min_length: int = 50,
                               max_length: int = 1200,
                               limit: Optional[int] = None) -> List[ProteinSequence]:
    """过滤和选择序列
    
    Args:
        sequences: 输入序列列表
        min_length: 最小序列长度
        max_length: 最大序列长度
        limit: 返回序列数量限制
        
    Returns:
        List[ProteinSequence]: 过滤后的序列列表
    """
```

### protflow.utils.validators

输入验证工具。

```python
def validate_protein_sequence(sequence: str) -> bool:
    """验证蛋白质序列
    
    Args:
        sequence: 氨基酸序列
        
    Returns:
        bool: 序列是否有效
        
    Example:
        >>> validate_protein_sequence("ACDEFGHIKLMNPQRSTVWY")
        True
        >>> validate_protein_sequence("ACDEFGHIKLMNPQRSTVWY123")
        False
    """

def validate_sequence_length(sequence: str, min_len: int, max_len: int) -> bool:
    """验证序列长度
    
    Args:
        sequence: 氨基酸序列
        min_len: 最小长度
        max_len: 最大长度
        
    Returns:
        bool: 长度是否在有效范围内
    """

def validate_file_path(file_path: Path) -> bool:
    """验证文件路径安全性
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 路径是否安全
        
    Note:
        防止目录遍历攻击，确保路径在项目目录内
    """
```

## 🔬 结构预测 API

### protflow.prediction.esm3_predict

ESM3结构预测模块。

```python
class StructurePrediction:
    """结构预测结果"""
    
    def __init__(self, sequence_id: str, pdb_content: str,
                 confidence_score: float, prediction_time: float):
        """初始化结构预测结果
        
        Args:
            sequence_id: 序列ID
            pdb_content: PDB格式内容
            confidence_score: 置信度分数
            prediction_time: 预测耗时（秒）
        """
    
    def save_pdb(self, output_file: Path) -> None:
        """保存PDB文件
        
        Args:
            output_file: 输出文件路径
        """
    
    @property
    def pdb_string(self) -> str:
        """获取PDB内容字符串"""

class ESM3Predictor:
    """ESM3结构预测器"""
    
    def __init__(self, config: ProtFlowConfig):
        """初始化预测器
        
        Args:
            config: ProtFlow配置对象
        """
    
    def load_model(self, model_name: str = "esm3-small") -> Any:
        """加载ESM3模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            Any: 加载的模型对象
            
        Raises:
            ModelLoadError: 模型加载失败
        """
    
    def predict_structure(self, sequence: ProteinSequence) -> StructurePrediction:
        """预测单个蛋白质结构
        
        Args:
            sequence: 蛋白质序列
            
        Returns:
            StructurePrediction: 结构预测结果
            
        Raises:
            PredictionError: 预测执行失败
        """
    
    def predict_batch(self, sequences: List[ProteinSequence]) -> List[StructurePrediction]:
        """批量预测蛋白质结构
        
        Args:
            sequences: 蛋白质序列列表
            
        Returns:
            List[StructurePrediction]: 预测结果列表
            
        Example:
            >>> predictor = ESM3Predictor(config)
            >>> model = predictor.load_model("esm3-small")
            >>> results = predictor.predict_batch(sequences)
        """

def predict_pdbs(model: Any, sequences: List[ProteinSequence], 
                output_dir: Path, config: ProtFlowConfig) -> int:
    """批量预测并保存PDB文件
    
    Args:
        model: ESM3模型对象
        sequences: 蛋白质序列列表
        output_dir: PDB输出目录
        config: 配置对象
        
    Returns:
        int: 成功预测的蛋白质数量
    """
```

### protflow.prediction.model_manager

模型生命周期管理。

```python
class ModelManager:
    """模型管理器，处理模型加载和缓存"""
    
    def __init__(self, config: ProtFlowConfig):
        """初始化模型管理器
        
        Args:
            config: ProtFlow配置对象
        """
    
    def load_model(self, model_name: str, device: str = "auto") -> Any:
        """加载模型
        
        Args:
            model_name: 模型名称
            device: 设备类型（auto, cpu, cuda）
            
        Returns:
            Any: 模型对象
        """
    
    def unload_model(self, model_name: str) -> None:
        """卸载模型，释放内存
        
        Args:
            model_name: 模型名称
        """
    
    def list_available_models(self) -> List[str]:
        """获取可用模型列表
        
        Returns:
            List[str]: 模型名称列表
        """
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取模型信息
        
        Args:
            model_name: 模型名称
            
        Returns:
            Dict[str, Any]: 模型信息字典
        """
```

## ⚗️ 分子对接 API

### protflow.docking.p2rank

P2Rank口袋检测模块。

```python
class Pocket:
    """结合口袋数据类"""
    
    def __init__(self, pocket_id: str, center: Tuple[float, float, float],
                 size: float, score: float):
        """初始化口袋
        
        Args:
            pocket_id: 口袋ID
            center: 中心坐标 (x, y, z)
            size: 口袋大小
            score: 置信度分数
        """

class PocketPrediction:
    """口袋预测结果"""
    
    def __init__(self, structure_id: str, pockets: List[Pocket]):
        """初始化预测结果
        
        Args:
            structure_id: 结构ID
            pockets: 口袋列表
        """
    
    def get_top_pockets(self, n: int = 3) -> List[Pocket]:
        """获取排名前N的口袋
        
        Args:
            n: 口袋数量
            
        Returns:
            List[Pocket]: 口袋列表
        """
    
    def save_predictions(self, output_file: Path) -> None:
        """保存预测结果到文件
        
        Args:
            output_file: 输出文件路径
        """

class P2RankDetector:
    """P2Rank口袋检测器"""
    
    def __init__(self, p2rank_path: Path, config: ProtFlowConfig):
        """初始化检测器
        
        Args:
            p2rank_path: P2Rank可执行文件路径
            config: ProtFlow配置对象
        """
    
    def detect_pockets(self, pdb_file: Path) -> PocketPrediction:
        """检测蛋白质结构中的结合口袋
        
        Args:
            pdb_file: PDB文件路径
            
        Returns:
            PocketPrediction: 口袋预测结果
            
        Raises:
            ToolExecutionError: P2Rank执行失败
        """
    
    def detect_pockets_batch(self, pdb_dir: Path, 
                           output_dir: Path) -> List[PocketPrediction]:
        """批量检测口袋
        
        Args:
            pdb_dir: PDB文件目录
            output_dir: 输出目录
            
        Returns:
            List[PocketPrediction]: 预测结果列表
        """

def run_p2rank_batch(pdb_dir: Path, output_dir: Path, 
                    p2rank_path: Path, config: ProtFlowConfig) -> int:
    """批量运行P2Rank口袋检测
    
    Args:
        pdb_dir: PDB文件目录
        output_dir: 输出目录
        p2rank_path: P2Rank路径
        config: 配置对象
        
    Returns:
        int: 成功处理的结构数量
    """
```

### protflow.docking.vina_dock

AutoDock Vina分子对接模块。

```python
class Ligand:
    """配体数据类"""
    
    def __init__(self, ligand_id: str, file_path: Path, 
                 smiles: Optional[str] = None):
        """初始化配体
        
        Args:
            ligand_id: 配体ID
            file_path: 配体文件路径
            smiles: SMILES字符串（可选）
        """

class DockingResult:
    """分子对接结果"""
    
    def __init__(self, protein_id: str, ligand_id: str,
                 binding_affinity: float, docked_pose: Path):
        """初始化对接结果
        
        Args:
            protein_id: 蛋白质ID
            ligand_id: 配体ID
            binding_affinity: 结合亲和力（kcal/mol）
            docked_pose: 对接构象文件路径
        """
    
    def get_binding_affinity(self) -> float:
        """获取结合亲和力"""
    
    def save_result(self, output_dir: Path) -> None:
        """保存对接结果"""

class VinaDockingEngine:
    """Vina分子对接引擎"""
    
    def __init__(self, vina_path: Path, config: ProtFlowConfig):
        """初始化对接引擎
        
        Args:
            vina_path: Vina可执行文件路径
            config: ProtFlow配置对象
        """
    
    def dock_ligand(self, protein_file: Path, ligand_file: Path,
                   pocket: Pocket, output_dir: Path) -> DockingResult:
        """执行分子对接
        
        Args:
            protein_file: 蛋白质PDB文件
            ligand_file: 配体文件
            pocket: 结合口袋信息
            output_dir: 输出目录
            
        Returns:
            DockingResult: 对接结果
            
        Raises:
            ToolExecutionError: Vina执行失败
        """
    
    def dock_batch(self, protein_files: List[Path], 
                  ligand_files: List[Path],
                  pockets: List[Pocket], 
                  output_dir: Path) -> List[DockingResult]:
        """批量分子对接
        
        Args:
            protein_files: 蛋白质文件列表
            ligand_files: 配体文件列表
            pockets: 口袋信息列表
            output_dir: 输出目录
            
        Returns:
            List[DockingResult]: 对接结果列表
        """

def dock_to_pockets(protein_file: Path, ligand_file: Path,
                   pockets_file: Path, output_dir: Path,
                   vina_path: Path, config: ProtFlowConfig) -> List[DockingResult]:
    """对接配体到多个口袋
    
    Args:
        protein_file: 蛋白质文件
        ligand_file: 配体文件
        pockets_file: 口袋预测结果文件
        output_dir: 输出目录
        vina_path: Vina路径
        config: 配置对象
        
    Returns:
        List[DockingResult]: 对接结果列表
    """
```

### protflow.docking.ligand_prep

配体准备模块。

```python
def smiles_to_pdbqt(smiles: str, output_file: Path, 
                   pH: float = 7.4) -> Path:
    """将SMILES字符串转换为PDBQT格式
    
    Args:
        smiles: SMILES字符串
        output_file: 输出文件路径
        pH: pH值（默认7.4）
        
    Returns:
        Path: PDBQT文件路径
        
    Raises:
        ToolExecutionError: 格式转换失败
        
    Example:
        >>> pdbqt_file = smiles_to_pdbqt("CCO", Path("ligand.pdbqt"))
    """

def prepare_ligand_from_file(input_file: Path, output_file: Path,
                            pH: float = 7.4) -> Path:
    """准备配体文件
    
    Args:
        input_file: 输入配体文件
        output_file: 输出文件路径
        pH: pH值
        
    Returns:
        Path: 准备好的配体文件路径
    """

def validate_ligand_file(file_path: Path) -> bool:
    """验证配体文件格式
    
    Args:
        file_path: 配体文件路径
        
    Returns:
        bool: 文件是否有效
    """
```

## 📊 可视化 API

### protflow.visualization.report_builder

报告生成模块。

```python
class ReportBuilder:
    """报告构建器"""
    
    def __init__(self, config: ProtFlowConfig):
        """初始化报告构建器
        
        Args:
            config: ProtFlow配置对象
        """
    
    def add_section(self, title: str, content: str) -> None:
        """添加报告章节
        
        Args:
            title: 章节标题
            content: 章节内容
        """
    
    def add_structure_image(self, pdb_file: Path, caption: str) -> None:
        """添加结构图像
        
        Args:
            pdb_file: PDB文件路径
            caption: 图像说明
        """
    
    def add_docking_results(self, results: List[DockingResult]) -> None:
        """添加对接结果
        
        Args:
            results: 对接结果列表
        """
    
    def generate_report(self, output_file: Path, 
                       format: str = "pdf") -> Path:
        """生成报告
        
        Args:
            output_file: 输出文件路径
            format: 报告格式（pdf, html, markdown）
            
        Returns:
            Path: 生成的报告文件路径
        """

def generate_analysis_report(results_dir: Path, output_file: Path,
                           config: ProtFlowConfig) -> Path:
    """生成分析结果报告
    
    Args:
        results_dir: 结果目录
        output_file: 输出文件路径
        config: 配置对象
        
    Returns:
        Path: 报告文件路径
    """
```

## 🛠️ 工具函数 API

### protflow.utils.file_utils

文件操作工具。

```python
def ensure_directory(path: Path) -> None:
    """确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    """

def safe_delete_file(file_path: Path) -> bool:
    """安全删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 删除是否成功
    """

def copy_file_safely(src: Path, dst: Path, 
                    overwrite: bool = False) -> None:
    """安全复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        overwrite: 是否覆盖已存在的文件
    """

def find_files_by_extension(directory: Path, 
                           extension: str) -> List[Path]:
    """按扩展名查找文件
    
    Args:
        directory: 搜索目录
        extension: 文件扩展名
        
    Returns:
        List[Path]: 找到的文件路径列表
    """
```

### protflow.utils.parallel

并行处理工具。

```python
class ParallelProcessor:
    """并行处理器"""
    
    def __init__(self, max_workers: int = None):
        """初始化并行处理器
        
        Args:
            max_workers: 最大工作进程数，默认为CPU核心数
        """
    
    def process_batch(self, items: List[Any], 
                     processing_func: Callable) -> List[Any]:
        """批量并行处理
        
        Args:
            items: 待处理项目列表
            processing_func: 处理函数
            
        Returns:
            List[Any]: 处理结果列表
        """

def run_parallel_tasks(tasks: List[Callable], 
                      max_workers: int = 4) -> List[Any]:
    """运行并行任务
    
    Args:
        tasks: 任务函数列表
        max_workers: 最大工作进程数
        
    Returns:
        List[Any]: 任务结果列表
    """
```

## 🔒 安全 API

### protflow.utils.security

安全验证工具。

```python
def validate_sequence_input(sequence: str) -> bool:
    """验证序列输入安全性
    
    Args:
        sequence: 输入序列
        
    Returns:
        bool: 序列是否安全
    """

def validate_file_path(file_path: Path) -> bool:
    """验证文件路径安全性
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 路径是否安全
    """

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除危险字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """

def check_dependencies_security() -> Dict[str, List[str]]:
    """检查依赖安全性
    
    Returns:
        Dict[str, List[str]]: 安全检查结果
    """
```

## 📈 性能监控 API

### protflow.utils.performance

性能监控工具。

```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, enable_logging: bool = True):
        """初始化性能监控器
        
        Args:
            enable_logging: 是否启用日志记录
        """
    
    def start_monitoring(self, task_name: str) -> None:
        """开始监控任务
        
        Args:
            task_name: 任务名称
        """
    
    def end_monitoring(self, task_name: str) -> Dict[str, Any]:
        """结束监控任务
        
        Args:
            task_name: 任务名称
            
        Returns:
            Dict[str, Any]: 性能数据
        """

def monitor_performance(func_name: str = None):
    """性能监控装饰器
    
    Args:
        func_name: 函数名称（可选）
        
    Returns:
        Callable: 装饰器函数
        
    Example:
        >>> @monitor_performance("structure_prediction")
        >>> def predict_structure(sequence):
        ...     # 预测逻辑
        ...     pass
    """
```

## 🔧 辅助函数

### 类型别名

```python
# 常用类型别名
from typing import Union, List, Dict, Optional, Any
from pathlib import Path

ProteinID = str
Sequence = str
PDBContent = str
SMILES = str
BindingAffinity = float
Coordinate3D = Tuple[float, float, float]
FilePath = Union[str, Path]
```

### 常量定义

```python
# 氨基酸常量
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
VALID_AMINO_ACIDS = set(AMINO_ACIDS)

# 默认配置值
DEFAULT_MIN_LENGTH = 50
DEFAULT_MAX_LENGTH = 1200
DEFAULT_MAX_SEQUENCES = 10
DEFAULT_MAX_WORKERS = 4

# 文件扩展名
SUPPORTED_SEQUENCE_FORMATS = [".fasta", ".faa", ".fa"]
SUPPORTED_STRUCTURE_FORMATS = [".pdb", ".cif"]
SUPPORTED_LIGAND_FORMATS = [".mol2", ".sdf", ".pdbqt"]
```

## 📝 使用示例

### 基础工作流示例

```python
from pathlib import Path
from protflow.core.config import load_config, ProtFlowConfig
from protflow.utils.seq_parser import SequenceParser, ProteinSequence
from protflow.prediction.esm3_predict import ESM3Predictor
from protflow.docking.p2rank import P2RankDetector
from protflow.docking.vina_dock import VinaDockingEngine

# 1. 加载配置
config = load_config(Path("config.json"))

# 2. 解析序列
parser = SequenceParser(config)
sequences = parser.parse_fasta(Path("proteins.faa"))

# 3. 结构预测
predictor = ESM3Predictor(config)
model = predictor.load_model("esm3-small")
predictions = predictor.predict_batch(sequences[:5])  # 预测前5个

# 4. 口袋检测
detector = P2RankDetector(Path("prank"), config)
pocket_results = []
for prediction in predictions:
    result = detector.detect_pockets(Path(f"{prediction.sequence_id}.pdb"))
    pocket_results.append(result)

# 5. 分子对接
engine = VinaDockingEngine(Path("vina"), config)
docking_results = []
for i, pockets in enumerate(pocket_results):
    if pockets.pockets:
        result = engine.dock_ligand(
            Path(f"{predictions[i].sequence_id}.pdb"),
            Path("ligand.pdbqt"),
            pockets.pockets[0],
            Path("docking_output")
        )
        docking_results.append(result)
```

### 并行处理示例

```python
from protflow.utils.parallel import ParallelProcessor
from protflow.prediction.esm3_predict import StructurePrediction

# 创建并行处理器
processor = ParallelProcessor(max_workers=8)

# 定义处理函数
def process_sequence(sequence: ProteinSequence) -> StructurePrediction:
    predictor = ESM3Predictor(config)
    return predictor.predict_structure(sequence)

# 并行处理
results = processor.process_batch(sequences, process_sequence)
```

### 性能监控示例

```python
from protflow.utils.performance import monitor_performance

@monitor_performance("structure_prediction")
def predict_with_monitoring(sequence: ProteinSequence) -> StructurePrediction:
    predictor = ESM3Predictor(config)
    return predictor.predict_structure(sequence)

# 使用装饰器函数
result = predict_with_monitoring(sequence)
```

---

**💡 提示**:

1. **错误处理**: 始终使用try-except块处理可能的异常
2. **日志记录**: 使用结构化的日志记录重要事件
3. **性能考虑**: 对于大批量处理，使用并行处理功能
4. **内存管理**: 及时卸载不再使用的模型以释放内存
5. **配置管理**: 使用统一的配置管理，避免硬编码参数

这个API参考提供了ProtFlow所有主要功能的详细说明，帮助开发者有效地使用库功能构建自定义工作流。