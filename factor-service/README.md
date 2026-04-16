# factor-service

因子分析与评分计算服务，提供技术指标计算、因子选股、评分权重配置、综合评分计算和回测验证能力。

## 功能特性

- **技术指标计算**：MA、EMA、MACD、RSI、KDJ、布林带等
- **因子选股**：支持自定义因子条件筛选股票
- **评分权重配置**：多因子加权评分
- **综合评分计算**：生成股票排名
- **回测验证**：IC分析、分组收益对比、敏感性测试

## 快速开始

### 环境要求

- Python 3.10+

### 安装依赖

```bash
cd factor-service
pip install -e .
```

### 配置

复制 `.env.example` 为 `.env`：

```env
SERVICE_PORT=8010
STOCK_SERVICE_URL=http://localhost:8008
```

### 启动服务

```bash
python run.py
```

服务默认运行在 `http://localhost:8010`

### API文档

启动后访问 `http://localhost:8010/docs` 查看API文档

## MCP工具

服务提供以下MCP工具：

### 指标模块
- `indicator_calculate` - 计算单只股票技术指标
- `indicator_batch` - 批量计算指标
- `indicator_list` - 获取支持的指标列表

### 因子模块
- `factor_screen` - 因子选股
- `factor_score` - 综合评分计算
- `factor_value` - 获取单只股票因子值

### 回测模块
- `backtest_run` - 执行完整回测
- `backtest_ic` - IC分析
- `backtest_group` - 分组收益对比
- `backtest_sensitivity` - 敏感性测试

## 注意事项

1. 服务依赖 stock-service (端口 8008) 提供行情数据
2. 本服务不存储数据，配置由 backend/stock_policy 管理