# ProtFlow 文档中心

欢迎使用ProtFlow文档中心！这里包含了使用ProtFlow进行蛋白质结构预测和分析所需的所有文档。

## 🚀 快速开始

新用户请从这里开始：
- [快速开始指南](user-guide/quick-start.md) - 5分钟上手ProtFlow
- [安装指南](user-guide/installation.md) - 详细安装步骤
- [Notebook索引指南](user-guide/notebook-index.md) - 所有Notebook的完整索引（[中文版](user-guide/notebook-index-zh.md)）和使用指南（[中文版](user-guide/notebook-index-zh.md)）
- [Notebook使用指南](user-guide/migration/notebook-usage.md) - 如何使用Jupyter Notebooks
- [故障排除指南](user-guide/tutorial/troubleshooting.md) - 常见问题解决方案

## 📖 用户指南

### 工作流程
- [Notebook索引指南](user-guide/notebook-index.md) - 所有Notebook的完整索引
- [Notebook使用指南](user-guide/migration/notebook-usage.md) - 如何使用Jupyter Notebooks
- [从Colab迁移](user-guide/migration/from-colab.md) - 从Google Colab迁移到服务器

### 核心工作流程
- [基因组注释到结构](user-guide/tutorial/genome-annotation-to-structure.md) - 完整的工作流程：Prokka → ESM3 → DALI
- [蛋白质结构预测](user-guide/tutorial/protein-structure-prediction.md) - 使用ESM3预测蛋白质结构
- [口袋检测](user-guide/tutorial/pocket-detection.md) - 使用P2Rank检测结合口袋
- [分子对接](user-guide/tutorial/ligand-docking.md) - 使用AutoDock Vina进行分子对接
- [基因簇分析](user-guide/tutorial/gene-cluster-analysis.md) - 使用antiSMASH分析生物合成基因簇

### 高级功能
- [批量分析](user-guide/tutorial/batch-analysis.md) - 大规模数据处理
- [结果比较](user-guide/tutorial/result-comparison.md) - 比较不同分析结果
- [性能优化](user-guide/tutorial/performance-tuning.md) - 优化分析性能

### 故障排除
- [常见问题](user-guide/tutorial/troubleshooting.md) - 常见问题解决方案

## ⚙️ 配置参考

- [配置概览](configuration/overview.md) - 配置文件结构和选项
- [配置示例](configuration/examples.md) - 各种使用场景的配置示例
- [服务器配置](configuration/server-config.md) - 服务器环境专用配置
- [性能调优](configuration/performance-tuning.md) - 性能优化配置

## 🔧 开发者指南

- [架构说明](developer-guide/architecture.md) - 项目架构设计
- [API参考](developer-guide/api-reference.md) - Python API文档
- [开发环境](developer-guide/development-setup.md) - 设置开发环境
- [贡献指南](developer-guide/contributing.md) - 如何为项目做贡献

## 🛠️ 工具文档

- [Makefile使用](tools/makefile.md) - 开发工具使用说明
- [部署指南](tools/deployment.md) - 服务器部署说明
- [脚本工具](tools/scripts/) - 各种实用脚本说明

## 📊 关于项目

- [项目总结](about/project-summary.md) - 项目整理总结
- [重构总结](about/refactoring-summary.md) - 代码重构过程总结
- [文档审计报告](audit/documentation-audit.md) - 文档整理审计报告
- [文档重组报告](audit/reorganization-report.md) - 文档重组完成报告
- [更新日志](about/changelog.md) - 版本更新记录
- [许可证](about/license.md) - 项目许可证信息
- [致谢](about/credits.md) - 项目贡献者

## 🔍 搜索和导航

### 按用户类型
- **新用户**：快速开始 → Notebook索引 → 用户指南
- **有经验用户**：配置参考 → 高级功能 → 性能优化
- **开发者**：开发者指南 → API参考 → 贡献指南
- **系统管理员**：部署指南 → 服务器配置 → 工具文档

### 按功能模块
- **基因组分析**：基因组注释 → 基因簇分析
- **结构分析**：结构预测 → 结构比对
- **分子对接**：口袋检测 → 分子对接
- **批量处理**：批量分析 → 结果比较
- **Notebook索引**：按编号快速找到对应笔记本
  - **00-09**: 核心工作流程
  - **10-19**: 独立分析工具
  - **20-29**: 结果分析工具

## 💡 使用提示

1. **文档版本**：确保查看的文档与您的ProtFlow版本匹配
2. **反馈建议**：如果发现文档问题，欢迎提交Issue或Pull Request
3. **更新频率**：文档会随着项目更新而定期更新
4. **搜索功能**：使用浏览器的搜索功能（Ctrl+F）快速查找内容

## 🆘 获取帮助

如果文档无法解决您的问题：
1. 查看[故障排除指南](user-guide/tutorial/troubleshooting.md)
2. 在GitHub上提交[Issue](https://github.com/AsagiriBeta/ProtFlow/issues)
3. 查看项目的[Wiki页面](https://github.com/AsagiriBeta/ProtFlow/wiki)

---

**📌 提示**：建议收藏此页面，作为使用ProtFlow的主要入口点。