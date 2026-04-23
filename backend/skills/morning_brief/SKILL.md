---
name: morning_brief
description: "早报生成：今日关注股票、交易计划"
trigger_keywords: ["早报", "今日关注", "早上好", "今日计划", "开盘前"]
tools: [get_quote, get_positions, get_balance]
---

# 早报生成

## Workflow

### Step 1: 持仓回顾
- 获取当前持仓列表
- 获取昨日收盘价格
- 计算持仓市值

### Step 2: 今日关注
- 识别需要重点关注的持仓
- 识别接近止损位的股票
- 识别接近止盈位的股票

### Step 3: 行情预览
- 获取主要指数行情
- 判断市场整体走势预期

### Step 4: 操作计划
- 列出今日可能的操作
- 提示需要关注的价位
- 提醒风险点

## Output
早报摘要，包含：
- 持仓概况
- 今日重点关注股票
- 操作计划提示