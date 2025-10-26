# 蛋白质结构预测、口袋识别、配体对接与BGC注释的模块化流程

一个模块化工具包：解析 GenBank 蛋白序列、用 ESM3-sm 预测结构、用 P2Rank 识别口袋、准备配体并用 Vina 对接、生成报告，并可选运行 antiSMASH——各步骤均可独立执行、互不强制依赖。

[English README](README.md)

本仓库支持在本地或 Google Colab 运行，主流程示例见 `ESM3_sm_pipeline-2.ipynb`，并提供命令行方式独立运行任意步骤。

## 模块化与命令行
- 包实现位于 `esm3_pipeline/`：
  - GenBank 解析（`seq_parser.py`）
  - ESM3-sm 预测（`esm3_predict.py`）
  - 口袋识别 P2Rank（`p2rank.py`）
  - 配体准备（`ligand_prep.py`）
  - Vina 对接（`vina_dock.py`）
  - 报告生成（`reporting.py`）
  - antiSMASH 可选分析（`antismash.py`）
- 命令行运行示例（各步骤可选）：

```bash
python -m scripts.runner --parse-gbk --predict --p2rank --vina --report \
  --gbk-dir ./esm3_pipeline/gbk_input --smiles "CCO" --limit 5
```

可选参数说明：
- `--parse-gbk` 解析 `--gbk-dir` 下的 `.gbk/.gbff`
- `--predict` 使用 ESM3-sm 产生 PDB 到 `esm3_pipeline/pdbs`
- `--p2rank` 口袋打分
- `--vina` 若存在配体与口袋结果则进行对接
- `--report` 生成 `esm3_results_report.pdf`
- `--antismash` 运行 antiSMASH（需已安装）

## antiSMASH（可选）
- 不包含在 `requirements.txt`，建议用 conda 安装；也可用 Docker。

简要安装与使用：
- 方案 A（推荐，Bioconda）
  ```zsh
  conda config --add channels conda-forge
  conda config --add channels bioconda
  conda create -y -n antismash antismash
  conda activate antismash
  download-antismash-databases
  # 可选一次性准备缓存
  antismash --prepare-data
  antismash --version
  ```
- 方案 B（Docker，全量镜像，含数据库，下载较大）
  ```zsh
  mkdir -p ~/bin
  curl -q https://dl.secondarymetabolites.org/releases/latest/docker-run_antismash-full > ~/bin/run_antismash
  chmod a+x ~/bin/run_antismash
  # 使用时务必使用绝对路径，且参数顺序固定：先输入文件，再输出目录
  run_antismash /绝对路径/输入.gbk /绝对路径/输出目录 --taxon bacteria
  ```
  注：若使用 lite 镜像，请另行下载数据库（同官网说明）。

- 在本仓库中运行 antiSMASH：
  ```zsh
  # 建议在已安装 antiSMASH 的 conda 环境中执行
  conda activate antismash
  python -m scripts.runner --antismash --gbk-dir ./esm3_pipeline/gbk_input
  ```
  输出位于 `esm3_pipeline/antismash_out`，通常包含 `index.html`。

常见问题（简要）：
- 找不到 antismash：确保已 `conda activate antismash`，并检查 `echo $PATH`。
- 第一次运行较慢或缺数据库：先执行 `download-antismash-databases` 与 `antismash --prepare-data`。
- Docker 路径：wrapper 需绝对路径，参数顺序固定：输入文件 → 输出目录。
- Apple Silicon：Bioconda 兼容；Docker 可能拉取 amd64 镜像，首次运行较慢。

### Apple Silicon（macOS arm64）说明
- 在 arm64 上，Bioconda 可能因为 `hmmer2` 没有 `osx-arm64` 版本而解算失败。
- 两种可行方案：
  1) 推荐使用 Docker wrapper（不需要 conda）：安装 Docker Desktop，然后按上文使用 `run_antismash`。本仓库代码会自动识别 wrapper。
  2) 使用 Rosetta x86_64 conda 环境：
     ```zsh
     softwareupdate --install-rosetta --agree-to-license # 如未安装
     arch -x86_64 zsh -c 'CONDA_SUBDIR=osx-64 conda create -y -n antismash antismash'
     conda activate antismash
     conda config --env --set subdir osx-64
     download-antismash-databases
     antismash --prepare-data && antismash --version
     ```

## 依赖与环境
- Python 包见 `requirements.txt`；Linux 上请按平台选择合适的 PyTorch 轮子（CPU/CUDA）。
- 系统工具：Java（P2Rank）、OpenBabel（格式转换与 PDBQT）、AutoDock Vina（对接）。
- macOS/Ubuntu 可使用脚本安装：
  - Ubuntu/Debian：`bash scripts/setup_ubuntu.sh`
  - macOS（Homebrew）：`bash scripts/setup_macos.sh`

### Hugging Face Token
- 访问 `esm3-sm-open-v1` 需要 Hugging Face Token：环境变量 `HF_TOKEN` 或在 notebook 里交互登录。

## Notebook 使用提示
- Colab 上启用 GPU 以加速 ESM3-sm；各单元可独立运行，步骤可跳过。
- notebook 已改为调用模块函数，功能保持不变但更易维护。

## 注意事项
- 若缺少外部工具（antiSMASH/Vina/OpenBabel/Java），相关步骤将自动跳过，不影响其他部分。
- P2Rank jar 会自动下载/定位，无需手动配置路径。
- CSV 坐标解析使用 `ast.literal_eval`，更安全。

## 许可证与第三方
本项目工作流依赖第三方工具（P2Rank、AutoDock Vina、OpenBabel、antiSMASH），它们拥有各自的许可证，请在分发前进行审阅。
