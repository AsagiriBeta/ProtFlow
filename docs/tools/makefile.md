# Makefile 使用指南

## 🎯 概述

ProtFlow项目包含一个功能丰富的Makefile，提供了开发、测试、部署等常用任务的自动化命令。

## 📋 可用命令

### 基础命令

#### `make help`
显示所有可用命令的帮助信息。
```bash
make help
```

#### `make install`
在生产模式下安装ProtFlow包。
```bash
make install
```

#### `make install-dev`
在开发模式下安装ProtFlow包，包含所有开发依赖。
```bash
make install-dev
```

### 测试命令

#### `make test`
运行完整的测试套件，包括代码覆盖率报告。
```bash
make test
```

#### `make test-quick`
运行快速测试，不包含代码覆盖率。
```bash
make test-quick
```

### 代码质量

#### `make lint`
运行代码检查工具（flake8和mypy）。
```bash
make lint
```

#### `make format`
自动格式化代码（使用black和isort）。
```bash
make format
```

#### `make format-check`
检查代码格式是否符合规范，不实际修改文件。
```bash
make format-check
```

### 清理和维护

#### `make clean`
清理构建产物和缓存文件。
```bash
make clean
```

清理内容包括：
- `__pycache__` 目录
- `.pyc` 和 `.pyo` 文件
- `.egg-info` 目录
- `build/` 和 `dist/` 目录
- 测试缓存和覆盖率报告

### 文档和运行

#### `make docs`
显示文档位置信息。
```bash
make docs
```

#### `make run`
显示ProtFlow CLI的帮助信息。
```bash
make run
```

#### `make example`
在示例数据上运行完整的分析流程。
```bash
make example
```

### 系统检查

#### `make check-deps`
检查系统依赖是否安装。
```bash
make check-deps
```

检查的工具包括：
- Java (必需)
- OpenBabel (必需)
- AutoDock Vina (必需)
- antiSMASH (可选)

### 系统设置

#### `make setup-macos`
在macOS系统上安装系统依赖。
```bash
make setup-macos
```

#### `make setup-ubuntu`
在Ubuntu/Debian系统上安装系统依赖。
```bash
make setup-ubuntu
```

## 🚀 常用工作流

### 开发工作流
```bash
# 1. 安装开发依赖
make install-dev

# 2. 运行测试
make test-quick

# 3. 检查代码质量
make lint

# 4. 格式化代码
make format

# 5. 运行完整测试
make test
```

### 部署前检查
```bash
# 1. 检查依赖
make check-deps

# 2. 运行测试
make test

# 3. 清理构建产物
make clean

# 4. 安装生产版本
make install
```

### 日常维护
```bash
# 清理缓存
make clean

# 检查代码格式
make format-check

# 快速测试
make test-quick
```

## ⚙️ 自定义配置

### 环境变量
Makefile支持以下环境变量：

```bash
# Python解释器路径
PYTHON=python3

# 虚拟环境路径
VENV_PATH=./venv

# 测试参数
TEST_ARGS=-v

# 代码格式化参数
BLACK_ARGS=--line-length 88
ISORT_ARGS=--profile black
```

### 自定义目标
您可以在项目根目录创建`Makefile.local`文件来添加自定义目标：

```makefile
# Makefile.local
my-custom-target:
	@echo "运行自定义任务"
	python my_script.py
```

## 🔧 故障排除

### 问题1: 权限错误
**症状**: `Permission denied`
**解决**:
```bash
chmod +x scripts/*.sh
```

### 问题2: 找不到命令
**症状**: `make: command not found`
**解决**: 安装make工具
```bash
# Ubuntu/Debian
sudo apt install build-essential

# macOS
xcode-select --install

# CentOS/RHEL
sudo yum install make
```

### 问题3: Python包导入错误
**症状**: `ModuleNotFoundError`
**解决**:
```bash
# 重新安装开发依赖
make install-dev

# 或者手动安装
pip install -e ".[dev]"
```

## 📊 性能优化

### 并行测试
```bash
# 使用pytest的并行测试功能
pip install pytest-xdist
make test PYTEST_ARGS="-n auto"
```

### 缓存利用
```bash
# 利用pytest缓存
make test PYTEST_ARGS="--lf"  # 只运行上次失败的测试
make test PYTEST_ARGS="--ff"  # 先运行上次失败的测试
```

## 🔍 相关文档

- [安装指南](../user-guide/installation.md) - 详细的安装步骤
- [开发环境配置](../developer-guide/development-setup.md) - 设置开发环境
- [测试文档](../developer-guide/testing.md) - 测试策略和最佳实践

---

**💡 提示**: 使用`make help`命令可以随时查看所有可用选项。建议在开始开发工作前运行`make check-deps`确保所有依赖都已正确安装。