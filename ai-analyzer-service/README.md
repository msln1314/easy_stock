# AI Analyzer Service

AI 智能分析服务，提供趋势分析、风险评估、投资建议等 AI 驱动的分析能力。

## 功能

- **趋势分析**: 结合评分和指标数据，分析股票趋势
- **风险评估**: 基于回测数据和波动性，评估投资风险
- **投资建议**: 综合趋势分析和风险评估，生成投资建议
- **模型管理**: 支持 Claude/OpenAI/Ollama 多模型切换

## 架构

- FastAPI + FastMCP 双接口模式（REST API + MCP SSE）
- 三层架构：services → MCP classes → MCP server → main.py
- 无数据持久化，数据从 factor-service 通过 MCP 获取
- 服务端口：8011

## 运行

```bash
pip install -e .
python run.py
```

## 接口

- REST API: `http://localhost:8011/api/v1/...`
- MCP SSE: `http://localhost:8011/mcp`
- API 文档: `http://localhost:8011/docs`
- 健康检查: `http://localhost:8011/health`

## 配置

参考 `.env.example` 配置环境变量。