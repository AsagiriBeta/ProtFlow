# ProtFlow 架构设计

本文档详细描述了ProtFlow项目的系统架构、模块设计和核心组件。

## 🏗️ 系统架构概览

ProtFlow采用分层架构设计，将蛋白质结构预测和分子对接流程分解为独立的、可重用的模块。

```
┌─────────────────────────────────────────────────────────────┐
│                    用户接口层                                │
├─────────────────┬─────────────────┬─────────────────────────┤
│   CLI脚本       │   Jupyter Notebooks    │   Python API        │
│  scripts/runner │ notebooks/*.ipynb     │  import protflow    │
└─────────────────┴─────────────────┴─────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    工作流编排层                              │
├─────────────────────────────────────────────────────────────┤
│  Pipeline orchestration, Configuration management, Logging  │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │Core Workflow │ │Config Manager│ │   Logger          │   │
│  │  Coordination│ │ (JSON/YAML)  │ │  (Structured)     │   │
│  └──────────────┘ └──────────────┘ └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    核心功能模块                              │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   序列处理    │   结构预测    │   分子对接    │   结果分析     │
│  ┌────────┐  │  ┌────────┐  │  ┌────────┐  │  ┌────────┐  │
│  │Seq Parse│  ││ESM3 Pred│  ││P2Rank    │  ││Reporting│  │
│  │Filter   │  ││          │  ││Vina Dock│  ││Analysis │  │
│  └────────┘  │  └────────┘  │  └────────┘  │  └────────┘  │
└──────────────┴──────────────┴──────────────┴───────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    工具接口层                                │
├──────────────┬──────────────┬──────────────┬───────────────┤
│    ESM3      │   P2Rank     │ AutoDock Vina│   antiSMASH   │
│  (AI Model)  │(Pocket Det.) │  (Docking)   │  (BGC Analysis)│
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## 📦 模块架构

### 1. 核心模块 (`protflow.core`)

**职责**: 提供基础架构支持，包括配置管理、日志记录、异常处理

```python
# 核心组件
protflow.core/
├── __init__.py
├── config.py          # 配置管理系统
├── logger.py          # 结构化日志
├── exceptions.py      # 自定义异常
└── pipeline.py        # 管道协调器
```

**关键类设计**:

```python
@dataclass
class ProtFlowConfig:
    """主配置类，统一管理所有配置选项"""
    base_dir: Path = Path("./outputs")
    max_sequences: int = 10
    min_seq_length: int = 50
    max_seq_length: int = 1200
    enable_cache: bool = True
    log_level: str = "INFO"
    
    # 工具路径配置
    p2rank_path: Optional[Path] = None
    vina_path: Optional[Path] = None
    
    # 性能配置
    max_workers: int = 4
    batch_size: int = 1
    
    def validate(self) -> bool:
        """配置验证"""
        if self.min_seq_length >= self.max_seq_length:
            raise ConfigurationError("序列长度范围无效")
        return True

class PipelineOrchestrator:
    """工作流协调器，管理各个步骤的执行"""
    
    def __init__(self, config: ProtFlowConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.steps: List[PipelineStep] = []
    
    def add_step(self, step: PipelineStep) -> None:
        """添加处理步骤"""
        self.steps.append(step)
    
    def execute(self, input_data: Any) -> PipelineResult:
        """执行完整管道"""
        result = PipelineResult()
        for step in self.steps:
            try:
                self.logger.info(f"执行步骤: {step.name}")
                input_data = step.execute(input_data)
                result.add_step_result(step.name, input_data)
            except Exception as e:
                self.logger.error(f"步骤 {step.name} 失败: {e}")
                raise PipelineExecutionError(f"步骤执行失败: {step.name}") from e
        return result
```

### 2. 序列处理模块 (`protflow.utils`)

**职责**: 序列文件的解析、验证、过滤和预处理

```python
protflow.utils/
├── __init__.py
├── seq_parser.py      # 序列解析器
├── validators.py      # 输入验证
└── file_utils.py      # 文件操作工具
```

**核心功能**:

```python
class SequenceParser:
    """序列文件解析器，支持多种格式"""
    
    def parse_genbank(self, file_path: Path) -> List[ProteinSequence]:
        """解析GenBank文件"""
        # 使用Biopython解析GenBank
        pass
    
    def parse_fasta(self, file_path: Path) -> List[ProteinSequence]:
        """解析FASTA文件"""
        # 标准FASTA解析
        pass
    
    def extract_proteins_from_gbk(self, gbk_dir: Path, output_file: Path) -> int:
        """从GenBank文件目录提取蛋白质序列"""
        # 批量处理GenBank文件
        pass

class SequenceValidator:
    """序列验证器"""
    
    VALID_AMINO_ACIDS = set("ACDEFGHIKLMNPQRSTVWY")
    
    @staticmethod
    def validate_protein_sequence(sequence: str) -> bool:
        """验证蛋白质序列"""
        sequence = sequence.upper()
        return all(aa in SequenceValidator.VALID_AMINO_ACIDS for aa in sequence)
    
    @staticmethod
    def validate_sequence_length(sequence: str, min_len: int, max_len: int) -> bool:
        """验证序列长度"""
        return min_len <= len(sequence) <= max_len
```

### 3. 结构预测模块 (`protflow.prediction`)

**职责**: 蛋白质三维结构预测，主要基于ESM3模型

```python
protflow.prediction/
├── __init__.py
├── esm3_predict.py    # ESM3结构预测
├── model_manager.py   # 模型生命周期管理
└── batch_processor.py # 批处理优化
```

**架构设计**:

```python
class ESM3ModelManager:
    """ESM3模型管理器，处理模型加载和缓存"""
    
    def __init__(self, config: ProtFlowConfig):
        self.config = config
        self.model_cache: Dict[str, Any] = {}
        self.logger = get_logger(__name__)
    
    def load_model(self, model_name: str) -> Any:
        """加载指定模型，支持缓存"""
        if model_name in self.model_cache:
            self.logger.info(f"使用缓存的模型: {model_name}")
            return self.model_cache[model_name]
        
        # 实际模型加载逻辑
        model = self._load_esm3_model(model_name)
        
        if self.config.enable_cache:
            self.model_cache[model_name] = model
        
        return model
    
    def _load_esm3_model(self, model_name: str) -> Any:
        """实际的ESM3模型加载"""
        # 检查HF_TOKEN
        if not os.getenv("HF_TOKEN"):
            raise ModelLoadError("HF_TOKEN环境变量未设置")
        
        # 模型加载逻辑
        pass

class StructurePredictor:
    """结构预测器，封装预测逻辑"""
    
    def __init__(self, model_manager: ESM3ModelManager):
        self.model_manager = model_manager
        self.logger = get_logger(__name__)
    
    def predict_structure(self, sequence: ProteinSequence) -> StructurePrediction:
        """预测单个蛋白质结构"""
        try:
            model = self.model_manager.load_model("esm3-small")
            # 实际预测逻辑
            return self._execute_prediction(model, sequence)
        except Exception as e:
            self.logger.error(f"结构预测失败 {sequence.id}: {e}")
            raise PredictionError(f"结构预测失败: {sequence.id}") from e
    
    def predict_batch(self, sequences: List[ProteinSequence]) -> List[StructurePrediction]:
        """批量结构预测"""
        results = []
        for sequence in sequences:
            try:
                result = self.predict_structure(sequence)
                results.append(result)
            except Exception as e:
                self.logger.warning(f"跳过失败的序列 {sequence.id}: {e}")
                continue
        return results
```

### 4. 分子对接模块 (`protflow.docking`)

**职责**: 结合口袋检测和分子对接

```python
protflow.docking/
├── __init__.py
├── p2rank.py          # P2Rank口袋检测
├── vina_dock.py       # AutoDock Vina对接
├── ligand_prep.py     # 配体准备
└── result_analysis.py # 结果分析
```

**关键组件**:

```python
class PocketDetector:
    """口袋检测器，基于P2Rank"""
    
    def __init__(self, p2rank_path: Path):
        self.p2rank_path = p2rank_path
        self.logger = get_logger(__name__)
    
    def detect_pockets(self, structure_file: Path, output_dir: Path) -> PocketPrediction:
        """检测蛋白质结构中的结合口袋"""
        # 验证输入文件
        if not structure_file.exists():
            raise FileNotFoundError(f"结构文件不存在: {structure_file}")
        
        # 构建P2Rank命令
        cmd = [
            str(self.p2rank_path),
            "-f", str(structure_file),
            "-o", str(output_dir),
            "-threads", str(4)
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ToolExecutionError(f"P2Rank执行失败: {result.stderr}")
        
        return self._parse_p2rank_output(output_dir)

class DockingEngine:
    """分子对接引擎"""
    
    def __init__(self, vina_path: Path):
        self.vina_path = vina_path
        self.logger = get_logger(__name__)
    
    def dock_ligand(self, protein_file: Path, ligand_file: Path, 
                   pocket: Pocket, output_dir: Path) -> DockingResult:
        """执行分子对接"""
        # 准备对接配置
        config = self._prepare_docking_config(protein_file, ligand_file, pocket)
        
        # 执行Vina对接
        cmd = [
            str(self.vina_path),
            "--receptor", str(protein_file),
            "--ligand", str(ligand_file),
            "--config", str(config),
            "--out", str(output_dir / "docked.pdbqt")
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise ToolExecutionError(f"Vina对接失败: {result.stderr}")
        
        return self._parse_docking_result(output_dir)
```

### 5. 可视化模块 (`protflow.visualization`)

**职责**: 结果可视化和报告生成

```python
protflow.visualization/
├── __init__.py
├── structure_viz.py   # 结构可视化
├── plot_generator.py  # 图表生成
└── report_builder.py  # 报告构建
```

## 🔧 设计模式

### 1. 策略模式 (Strategy Pattern)

用于不同的序列过滤策略：

```python
class FilterStrategy(ABC):
    """过滤策略基类"""
    
    @abstractmethod
    def filter(self, sequences: List[ProteinSequence]) -> List[ProteinSequence]:
        pass

class LengthFilter(FilterStrategy):
    """长度过滤策略"""
    
    def __init__(self, min_length: int, max_length: int):
        self.min_length = min_length
        self.max_length = max_length
    
    def filter(self, sequences: List[ProteinSequence]) -> List[ProteinSequence]:
        return [s for s in sequences if self.min_length <= len(s.sequence) <= self.max_length]

class QualityFilter(FilterStrategy):
    """质量过滤策略"""
    
    def filter(self, sequences: List[ProteinSequence]) -> List[ProteinSequence]:
        # 基于序列质量分数过滤
        return [s for s in sequences if s.quality_score > 0.8]
```

### 2. 工厂模式 (Factory Pattern)

用于创建不同类型的预测器：

```python
class PredictorFactory:
    """预测器工厂"""
    
    @staticmethod
    def create_predictor(predictor_type: str, config: ProtFlowConfig) -> Predictor:
        """创建指定类型的预测器"""
        if predictor_type == "esm3":
            return ESM3Predictor(config)
        elif predictor_type == "esm2":
            return ESM2Predictor(config)
        elif predictor_type == "alphafold":
            return AlphaFoldPredictor(config)
        else:
            raise ValueError(f"不支持的预测器类型: {predictor_type}")
```

### 3. 观察者模式 (Observer Pattern)

用于进度报告和事件通知：

```python
class ProgressObserver(ABC):
    """进度观察者"""
    
    @abstractmethod
    def update(self, event: ProgressEvent) -> None:
        pass

class LoggingObserver(ProgressObserver):
    """日志记录观察者"""
    
    def update(self, event: ProgressEvent) -> None:
        logger.info(f"进度更新: {event.step_name} - {event.progress}%")

class ProgressBarObserver(ProgressObserver):
    """进度条观察者"""
    
    def __init__(self, total_steps: int):
        self.progress_bar = tqdm(total=total_steps)
    
    def update(self, event: ProgressEvent) -> None:
        if event.progress == 100:
            self.progress_bar.update(1)
```

## 📊 数据流架构

### 输入数据处理流程

```
GenBank Files → SequenceParser → Validation → Filter → ProteinSequences
     ↓
FASTA Files → SequenceParser → Validation → Filter → ProteinSequences
```

### 结构预测流程

```
ProteinSequences → ESM3Predictor → StructurePredictions → PDB Files
     ↓                                          ↓
ModelManager ←── Cache ←── Model Loading ←── HuggingFace Hub
```

### 分子对接流程

```
PDB Files → PocketDetector → Pockets → DockingEngine → DockingResults
                ↓              ↓           ↓              ↓
            P2Rank Tool → Analysis → Vina Tool → Analysis → Reports
```

## 🔒 错误处理和容错

### 异常层次结构

```python
class ProtFlowException(Exception):
    """基础异常类"""
    pass

class ConfigurationError(ProtFlowException):
    """配置错误"""
    pass

class ValidationError(ProtFlowException):
    """验证错误"""
    pass

class ModelLoadError(ProtFlowException):
    """模型加载错误"""
    pass

class PredictionError(ProtFlowException):
    """预测错误"""
    pass

class ToolExecutionError(ProtFlowException):
    """工具执行错误"""
    pass
```

### 重试机制

```python
from functools import wraps
import time

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # 指数退避
            return None
        return wrapper
    return decorator
```

## 🚀 性能优化

### 并行处理

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

class ParallelProcessor:
    """并行处理器"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
    
    def process_batch(self, items: List[Any], processing_func: Callable) -> List[Any]:
        """批量并行处理"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_item = {
                executor.submit(processing_func, item): item 
                for item in items
            }
            
            # 收集结果
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"处理项失败: {e}")
                    continue
        
        return results
```

### 缓存策略

```python
from functools import lru_cache
import hashlib
import pickle

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_cache_key(self, data: Any) -> str:
        """生成缓存键"""
        data_str = pickle.dumps(data)
        return hashlib.md5(data_str).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        cache_file = self.cache_dir / f"{key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(value, f)
```

## 📈 可扩展性设计

### 插件架构

```python
class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, ProtFlowPlugin] = {}
    
    def register_plugin(self, plugin: ProtFlowPlugin) -> None:
        """注册插件"""
        self.plugins[plugin.get_name()] = plugin
    
    def execute_plugin(self, plugin_name: str, data: Any) -> Any:
        """执行插件"""
        if plugin_name not in self.plugins:
            raise ValueError(f"插件不存在: {plugin_name}")
        
        plugin = self.plugins[plugin_name]
        return plugin.process(data)
```

### 配置热重载

```python
class ConfigWatcher:
    """配置文件监视器"""
    
    def __init__(self, config_file: Path, callback: Callable):
        self.config_file = config_file
        self.callback = callback
        self.last_modified = None
    
    def check_for_changes(self) -> bool:
        """检查配置变更"""
        if not self.config_file.exists():
            return False
        
        current_modified = self.config_file.stat().st_mtime
        if self.last_modified is None:
            self.last_modified = current_modified
            return False
        
        if current_modified != self.last_modified:
            self.last_modified = current_modified
            self.callback()
            return True
        
        return False
```

## 🔐 安全考虑

### 输入验证

```python
import re
from pathlib import Path

class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def validate_sequence_input(sequence: str) -> bool:
        """验证序列输入"""
        # 只允许标准氨基酸字符
        valid_pattern = re.compile(r'^[ACDEFGHIKLMNPQRSTVWY]+$', re.IGNORECASE)
        return bool(valid_pattern.match(sequence))
    
    @staticmethod
    def validate_file_path(file_path: Path) -> bool:
        """验证文件路径"""
        # 防止目录遍历攻击
        resolved = file_path.resolve()
        project_root = Path.cwd().resolve()
        
        try:
            resolved.relative_to(project_root)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名"""
        # 移除危险字符
        return re.sub(r'[^\w\-_.]', '_', filename)
```

---

**💡 设计原则**:

1. **单一职责**: 每个模块只负责一个功能领域
2. **依赖倒置**: 依赖抽象而非具体实现
3. **开闭原则**: 对扩展开放，对修改关闭
4. **接口隔离**: 提供专门的接口而非通用接口
5. **错误隔离**: 防止错误在模块间传播

这个架构设计确保了ProtFlow的可维护性、可扩展性和可靠性，同时保持了足够的灵活性来适应不同的使用场景和需求变化。