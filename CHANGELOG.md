# 更新日志

## v1.1.0 (2026-01-12)

### 🎉 新功能

- **集成 Finnhub API**：添加国际财经新闻源
  - 支持综合新闻（General）
  - 支持外汇新闻（Forex）
  - 支持加密货币新闻（Crypto）
  - 支持并购新闻（Merger）
- **自动加载 .env 文件**：使用 python-dotenv 自动加载环境变量
- **灵活配置**：TuShare 和 Finnhub 均为可选，至少启用一个即可

### ✨ 改进

- 优化新闻推送格式，区分国内和国际新闻
- 改进日志输出，更清晰地显示新闻来源
- 增强错误处理，提高稳定性

### 📚 文档

- 更新 README.md，添加 Finnhub 配置说明
- 更新 .env.example，添加 Finnhub Token 配置
- 新增 test_finnhub.py 测试脚本
- 新增 CHANGELOG.md 更新日志

### 🔧 技术细节

- 新增 `FinnhubCollector` 类处理 Finnhub API
- 重构 `NewsCollector` 为 `TuShareCollector`
- 优化新闻去重机制，支持多源新闻
- 改进异步处理逻辑

---

## v1.0.0 (2024-01-12)

### 🎉 初始版本

- 集成 TuShare 新闻接口
- 支持 9 个国内财经新闻来源
- 实时推送到电报机器人
- 智能去重机制
- 完善的错误处理和日志记录
- 多种部署方式（直接运行、systemd、Docker）
- 完整的项目文档
