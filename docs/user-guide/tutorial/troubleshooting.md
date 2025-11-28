# 故障排除指南

本指南帮助您解决使用ProtFlow过程中遇到的常见问题。

## 🔧 环境配置问题

### Java环境缺失
**问题**: `Java not found` 或 P2Rank无法运行
**解决**:
```bash
# Ubuntu/Debian
sudo apt install default-jre

# macOS
brew install openjdk

# 验证安装
java -version
```

### OpenBabel未安装
**问题**: 化学格式转换失败
**解决**:
```bash
# Ubuntu/Debian
sudo apt install openbabel

# macOS
brew install open-babel

# 验证安装
obabel -V
```

### AutoDock Vina缺失
**问题**: 分子对接步骤失败
**解决**:
```bash
# Ubuntu/Debian
sudo apt install autodock-vina

# macOS
brew install autodock-vina

# 验证安装
vina --help
```

## 🚀 模型和依赖问题

### ESM3模型加载失败
**问题**: `HF_TOKEN`相关错误或模型无法下载
**解决**:
1. 获取HuggingFace Token:
   - 访问 [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - 创建新的访问令牌
2. 设置环境变量:
```bash
export HF_TOKEN=hf_your_token_here
```

### GPU内存不足
**问题**: CUDA out of memory错误
**解决**:
```bash
# 减少处理序列数量
python -m scripts.runner --predict --limit 3

# 调整序列长度范围
python -m scripts.runner --predict --min-length 100 --max-length 500
```

### CUDA环境配置
**问题**: PyTorch无法检测到CUDA
**解决**:
```bash
# 检查CUDA可用性
python -c "import torch; print(torch.cuda.is_available())"

# 运行CUDA环境配置脚本（远程服务器）
chmod +x setup_cuda_env.sh
./setup_cuda_env.sh ~/jupyter-env-3.12
```

## 📁 文件和路径问题

### 输入文件缺失
**问题**: 找不到GenBank文件或序列文件
**解决**:
```bash
# 检查默认输入目录
ls -la ./esm3_pipeline/gbk_input/

# 指定输入目录
python -m scripts.runner --parse-gbk --gbk-dir /path/to/your/gbk/files
```

### 输出目录权限
**问题**: 无法创建输出文件或目录
**解决**:
```bash
# 检查目录权限
ls -la ./outputs/

# 创建输出目录并设置权限
mkdir -p outputs/pdbs outputs/reports
chmod 755 outputs/
```

### 配置文件错误
**问题**: JSON配置文件格式错误或选项无效
**解决**:
```bash
# 验证JSON格式
python -m json.tool config.json

# 使用示例配置作为模板
cp config/examples/standard.json config.json
# 然后编辑config.json
```

## 🔄 工作流执行问题

### 步骤执行失败
**问题**: 某个特定步骤（如预测、对接）失败
**解决**:
```bash
# 启用调试模式获取详细信息
python -m scripts.runner --log-level DEBUG --predict --limit 1

# 单独执行失败步骤进行测试
python -m scripts.runner --predict --limit 1  # 只运行预测
python -m scripts.runner --p2rank            # 只运行口袋检测
```

### 并行处理错误
**问题**: 多进程处理时出现错误
**解决**:
```bash
# 禁用并行处理进行测试
python -m scripts.runner --predict --limit 5 --workers 1

# 逐步增加工作进程
python -m scripts.runner --predict --limit 10 --workers 2
```

### 内存使用过高
**问题**: 系统内存不足，处理缓慢
**解决**:
```bash
# 减少批处理大小
python -m scripts.runner --predict --limit 2 --batch-size 1

# 禁用缓存以节省内存
python -m scripts.runner --predict --no-cache
```

## 📊 结果分析问题

### 输出文件为空
**问题**: 生成的报告或结果文件为空
**解决**:
```bash
# 检查日志文件
tail -f logs/protflow.log

# 验证输入数据
cat proteins.faa | head -n 20

# 检查中间结果
ls -la ./pdbs/*.pdb
```

### 可视化失败
**问题**: 结构可视化或图表生成失败
**解决**:
```bash
# 检查可视化依赖
pip install matplotlib seaborn plotly

# 手动运行可视化脚本
python scripts/visualize_results.py ./outputs/analysis/
```

## 🛠️ 调试工具和技巧

### 启用详细日志
```bash
# 设置调试级别日志
export PROTFLOW_LOG_LEVEL=DEBUG

# 同时输出到文件
python -m scripts.runner --log-file debug.log --predict --limit 1
```

### 检查依赖版本
```bash
# 运行依赖检查脚本
python scripts/check_deps.py

# 手动检查关键依赖
python -c "import esm; print(esm.__version__)"
python -c "import torch; print(torch.__version__)"
```

### 验证安装
```bash
# 测试基本导入
python -c "from protflow.utils import config; print('✓ ProtFlow导入成功')"

# 测试ESM3加载（小模型）
python -c "from protflow.prediction.esm3_predict import load_esm3_small; print('✓ ESM3模块导入成功')"
```

## 🆘 获取额外帮助

如果以上解决方案无法解决您的问题：

1. **查看详细日志**: 检查 `logs/` 目录下的日志文件
2. **提交Issue**: 在GitHub仓库提交[Issue](https://github.com/AsagiriBeta/ProtFlow/issues)
3. **社区支持**: 查看项目的[Wiki页面](https://github.com/AsagiriBeta/ProtFlow/wiki)
4. **邮件联系**: 联系项目维护者获取支持

## 🔍 预防性维护

### 定期更新
```bash
# 更新ProtFlow
git pull origin main
pip install -r requirements.txt --upgrade

# 更新数据库和模型
python scripts/update_databases.py
```

### 环境清理
```bash
# 清理临时文件
rm -rf tmp/* cache/*

# 清理旧的结果文件（谨慎操作）
find outputs/ -name "*.tmp" -delete
```

### 备份重要数据
```bash
# 备份配置文件
cp config.json config.json.backup

# 备份重要结果
tar -czf results_backup.tar.gz outputs/
```

---

**💡 提示**: 遇到问题时，首先检查日志文件，然后按照本指南逐步排查。大多数问题都与环境配置或依赖缺失有关。