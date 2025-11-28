# ProtFlow - 服务器版生物信息学分析平台

专为CUDA 13服务器环境优化的蛋白质结构预测与分析工作流

## 🏗️ 项目结构

```
ProtFlow/
├── notebooks/                    # Jupyter notebooks 分类组织
│   ├── core/                    # 核心工作流程 (00-09)
│   │   ├── 00_genome_annotation_to_structure.ipynb    # 基因组→结构完整流程
│   │   ├── 01_protein_structure_prediction.ipynb      # 蛋白质结构预测
│   │   ├── 02_pocket_detection_p2rank.ipynb           # 口袋检测
│   │   └── 03_ligand_docking_vina.ipynb               # 分子对接
│   ├── tools/                   # 独立工具 (10-19)
│   │   ├── 10_genome_annotation_prokka.ipynb          # Prokka注释
│   │   ├── 11_protein_structure_esm3.ipynb            # ESM3结构预测
│   │   ├── 12_structure_alignment_dali.ipynb          # DALI结构比对
│   │   └── 13_biosynthetic_cluster_antismash.ipynb    # antiSMASH分析
│   └── analysis/                # 分析工具 (20-29)
│       ├── 20_cds_annotation_comparison.ipynb         # CDS注释比较
│       └── 21_batch_structure_analysis.ipynb          # 批量结构分析
├── src/protflow/                # Python源代码
├── config/                      # 配置文件
├── data/                        # 输入数据
└── outputs/                     # 输出结果
```

## 🚀 快速开始

### 1. 环境要求
- **操作系统**: Linux (推荐Ubuntu 20.04+)
- **CUDA版本**: 13.0+
- **Python**: 3.8+
- **内存**: 建议32GB+
- **存储**: 建议100GB+ 可用空间

### 2. 安装步骤

```bash
# 克隆项目
git clone https://github.com/AsagiriBeta/ProtFlow.git
cd ProtFlow

# 创建虚拟环境
python3 -m venv protflow-env
source protflow-env/bin/activate

# 安装依赖
pip install -r requirements.txt

# 验证CUDA环境
python scripts/check_cuda.py
```

### 3. 配置环境

```bash
# 复制配置文件
cp config/config.example.json config/config.json

# 编辑配置（根据你的GPU和内存调整）
nano config/config.json

# 设置环境变量
export HF_TOKEN=your_huggingface_token
export CUDA_VISIBLE_DEVICES=0  # 使用第一个GPU
```

### 4. 启动JupyterLab

```bash
# 启动JupyterLab
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# 或者使用后台运行
nohup jupyter lab --ip=0.0.0.0 --port=8888 --no-browser > jupyter.log 2>&1 &
```

## 📋 工作流程选择

### 🔬 新基因组分析（推荐顺序）
1. **00_genome_annotation_to_structure.ipynb** - 完整流程
   - 输入: FNA核酸序列
   - 输出: 预测结构和功能注释
   - 时间: 2-6小时（取决于基因组大小）

### 🧬 单独功能分析
- **结构预测**: 01_protein_structure_prediction.ipynb
- **口袋检测**: 02_pocket_detection_p2rank.ipynb  
- **分子对接**: 03_ligand_docking_vina.ipynb
- **基因组注释**: 10_genome_annotation_prokka.ipynb
- **基因簇分析**: 13_biosynthetic_cluster_antismash.ipynb

### 📊 比较分析
- **CDS比较**: 20_cds_annotation_comparison.ipynb
- **批量分析**: 21_batch_structure_analysis.ipynb

## ⚙️ 配置文件说明

主要配置项：
```json
{
  "base_dir": "./outputs",           // 输出目录
  "data_dir": "./data",              // 输入数据目录
  "cuda_version": "13.0",            // CUDA版本
  "max_sequences": 50,               // 最大序列数
  "esm3_model": "esm3-sm-open-v1",   // ESM3模型
  "gpu_memory_fraction": 0.8,        // GPU内存使用比例
  "parallel_predictions": true,      // 并行预测
  "max_workers": 4                   // 最大工作线程
}
```

完整配置说明见: [config/CONFIG_README.md](config/CONFIG_README.md)

## 🛠️ 依赖管理

### CUDA 13环境配置
```bash
# 检查CUDA版本
nvcc --version

# 安装CUDA 13支持的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# 验证GPU可用性
python -c "import torch; print(torch.cuda.is_available())"
```

### 系统依赖
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y openjdk-11-jre openbabel autodock-vina

# 可选: Prokka依赖
sudo apt install -y bioperl libxml-simple-perl libdigest-md5-perl
```

## 🔧 常见问题

### Q: GPU内存不足
**A**: 
- 减少`max_sequences`配置
- 降低`gpu_memory_fraction`到0.6
- 使用更小的ESM3模型

### Q: 运行时间过长
**A**:
- 启用`parallel_predictions`
- 增加`max_workers`
- 使用SSD存储

### Q: 依赖包冲突
**A**:
- 使用干净的虚拟环境
- 按requirements.txt顺序安装
- 检查CUDA兼容性

### Q: JupyterLab无法连接GPU
**A**:
- 检查`CUDA_VISIBLE_DEVICES`设置
- 验证NVIDIA驱动安装
- 运行`nvidia-smi`确认GPU状态

## 🔄 从Colab迁移

### 主要变化
1. **无需Colab特定代码** - 所有notebook已移除Colab依赖
2. **本地文件系统** - 直接使用服务器路径，无需上传/下载
3. **持久化环境** - 安装一次，永久使用
4. **批量处理** - 支持大规模数据分析

### 迁移步骤
1. 将数据文件上传到服务器的`data/`目录
2. 更新notebook中的文件路径
3. 根据需要调整配置参数
4. 按顺序运行notebook

## 📈 性能优化建议

### 硬件优化
- **GPU**: RTX 4090或A100（24GB+显存）
- **内存**: 64GB+ DDR4
- **存储**: NVMe SSD 1TB+
- **CPU**: 16核+（AMD EPYC或Intel Xeon）

### 软件优化
- 启用并行处理
- 使用缓存机制
- 定期清理临时文件
- 监控GPU使用率

## 📞 技术支持

- 📧 邮箱: your-email@example.com
- 💬 Issues: [GitHub Issues](https://github.com/AsagiriBeta/ProtFlow/issues)
- 📖 文档: [项目Wiki](https://github.com/AsagiriBeta/ProtFlow/wiki)

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- ESM3团队提供优秀的蛋白质结构预测模型
- P2Rank和AutoDock Vina开发团队
- 所有开源贡献者

---

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**