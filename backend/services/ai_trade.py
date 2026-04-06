"""
AI交易服务模块
使用OpenAI Function Calling实现自然语言交易
"""
import json
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from loguru import logger

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from core.qmt_client import qmt_client
from services.config import SysConfigService


async def get_ai_config(key: str, default: str = "") -> str:
    """从数据库获取AI配置"""
    service = SysConfigService()
    value = await service.get_config_value(key)
    return value if value else default


class AITradeService:
    """AI交易服务"""

    def __init__(self):
        self.client = None
        self.model = OPENAI_MODEL

    async def _init_client(self):
        """初始化OpenAI客户端（从数据库读取配置）"""
        api_key = await get_ai_config("ai.openai_api_key", OPENAI_API_KEY)
        base_url = await get_ai_config("ai.openai_base_url", OPENAI_BASE_URL)
        model = await get_ai_config("ai.openai_model", OPENAI_MODEL)

        if not api_key:
            raise ValueError("未配置OpenAI API Key，请在系统配置中添加 ai.openai_api_key")

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

        # 定义可用的函数工具
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "buy_stock",
                    "description": "买入股票。用户可以说股票名称或代码。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_code": {
                                "type": "string",
                                "description": "股票代码，如000001、600519"
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "买入数量（股），必须是100的整数倍"
                            },
                            "price": {
                                "type": "number",
                                "description": "委托价格，不填则使用涨停价快速买入"
                            }
                        },
                        "required": ["stock_code", "quantity"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "sell_stock",
                    "description": "卖出股票。用户可以说股票名称或代码。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_code": {
                                "type": "string",
                                "description": "股票代码"
                            },
                            "quantity": {
                                "type": "integer",
                                "description": "卖出数量（股），必须是100的整数倍"
                            },
                            "price": {
                                "type": "number",
                                "description": "委托价格，不填则使用跌停价快速卖出"
                            }
                        },
                        "required": ["stock_code", "quantity"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_quote",
                    "description": "获取股票实时行情信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["stock_code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_positions",
                    "description": "获取当前持仓列表",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_balance",
                    "description": "获取账户资金信息",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

        # 系统提示词
        self.system_prompt = """你是一个专业的股票交易助手。你可以帮助用户：
1. 查询股票行情（如：平安银行现在多少钱）
2. 查看持仓（如：我的持仓）
3. 查看账户资金（如：账户余额）
4. 买入股票（如：买入平安银行100股）
5. 卖出股票（如：卖出000001的100股）

注意事项：
- 买入数量必须是100的整数倍
- 交易时间：工作日9:30-11:30, 13:00-15:00
- 如果用户没有指定价格，买入默认使用涨停价（快速成交），卖出使用跌停价
- 股票代码6开头是上海，0/3开头是深圳

请用简洁的中文回复。"""

    async def chat(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户消息

        Args:
            message: 用户消息
            context: 上下文信息（持仓、资金等）

        Returns:
            AI响应结果
        """
        try:
            # 初始化客户端
            if not self.client:
                await self._init_client()

            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]

            # 添加上下文信息
            if context:
                context_msg = f"当前用户信息：\n"
                if context.get("positions"):
                    context_msg += f"持仓：{json.dumps(context['positions'], ensure_ascii=False)}\n"
                if context.get("balance"):
                    context_msg += f"资金：{json.dumps(context['balance'], ensure_ascii=False)}\n"
                messages.append({"role": "system", "content": context_msg})

            messages.append({"role": "user", "content": message})

            # 调用OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # 检查是否需要调用函数
            if assistant_message.tool_calls:
                # 处理函数调用
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # 执行函数
                    result = await self._execute_function(function_name, function_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": json.dumps(result, ensure_ascii=False)
                    })

                # 将函数结果发回给AI生成最终回复
                messages.append(assistant_message)
                messages.extend(tool_results)

                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )

                return {
                    "role": "assistant",
                    "content": final_response.choices[0].message.content,
                    "function_called": function_name if len(assistant_message.tool_calls) == 1 else None,
                    "function_result": tool_results[0]["content"] if len(tool_results) == 1 else None
                }

            return {
                "role": "assistant",
                "content": assistant_message.content or "抱歉，我没有理解您的请求。"
            }

        except Exception as e:
            logger.error(f"AI聊天失败: {e}")
            return {
                "role": "assistant",
                "content": f"抱歉，处理您的请求时出现错误：{str(e)}"
            }

    async def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行函数调用"""
        try:
            if function_name == "buy_stock":
                return await self._buy_stock(
                    args.get("stock_code"),
                    args.get("quantity"),
                    args.get("price")
                )

            elif function_name == "sell_stock":
                return await self._sell_stock(
                    args.get("stock_code"),
                    args.get("quantity"),
                    args.get("price")
                )

            elif function_name == "get_quote":
                # 检查QMT是否开启
                qmt_enabled = await get_ai_config("ai.qmt_enabled", "false")
                if qmt_enabled.lower() != "true":
                    return {"success": False, "error": "QMT交易未开启，请在系统配置中开启 ai.qmt_enabled"}
                return await self._get_quote(args.get("stock_code"))

            elif function_name == "get_positions":
                # 检查QMT是否开启
                qmt_enabled = await get_ai_config("ai.qmt_enabled", "false")
                if qmt_enabled.lower() != "true":
                    return {"success": False, "error": "QMT交易未开启，请在系统配置中开启 ai.qmt_enabled"}
                return await self._get_positions()

            elif function_name == "get_balance":
                # 检查QMT是否开启
                qmt_enabled = await get_ai_config("ai.qmt_enabled", "false")
                if qmt_enabled.lower() != "true":
                    return {"success": False, "error": "QMT交易未开启，请在系统配置中开启 ai.qmt_enabled"}
                return await self._get_balance()

            else:
                return {"success": False, "error": f"未知函数: {function_name}"}

        except Exception as e:
            logger.error(f"执行函数失败: {function_name}, {e}")
            return {"success": False, "error": str(e)}

    async def _buy_stock(self, stock_code: str, quantity: int, price: float = None) -> Dict[str, Any]:
        """买入股票"""
        # 检查QMT是否开启
        qmt_enabled = await get_ai_config("ai.qmt_enabled", "false")
        if qmt_enabled.lower() != "true":
            return {"success": False, "error": "QMT交易未开启，请在系统配置中开启 ai.qmt_enabled"}

        # 检查交易时间
        trade_status = await qmt_client.get_trade_status()
        if not trade_status.get("is_trade_time"):
            return {
                "success": False,
                "error": "当前非交易时间",
                "next_trade_time": trade_status.get("next_trade_time")
            }

        # 转换股票代码格式
        qmt_code = self._convert_stock_code(stock_code)

        # 获取行情
        quote = await qmt_client.get_stock_quote(qmt_code)
        if not quote or not quote.get("price"):
            return {"success": False, "error": f"无法获取 {stock_code} 的行情数据"}

        # 如果没有指定价格，使用涨停价快速买入
        if not price:
            price = quote.get("limit_up", quote.get("price", 0))

        result = await qmt_client.buy_stock(
            stock_code=qmt_code,
            price=price,
            quantity=quantity,
            order_type="limit"
        )

        return {
            "success": result.get("success", True),
            "stock_code": stock_code,
            "stock_name": quote.get("stock_name", ""),
            "price": price,
            "quantity": quantity,
            "amount": price * quantity,
            "order_id": result.get("order_id"),
            "message": result.get("message", "买入委托成功")
        }

    async def _sell_stock(self, stock_code: str, quantity: int, price: float = None) -> Dict[str, Any]:
        """卖出股票"""
        # 检查QMT是否开启
        qmt_enabled = await get_ai_config("ai.qmt_enabled", "false")
        if qmt_enabled.lower() != "true":
            return {"success": False, "error": "QMT交易未开启，请在系统配置中开启 ai.qmt_enabled"}

        # 检查交易时间
        trade_status = await qmt_client.get_trade_status()
        if not trade_status.get("is_trade_time"):
            return {
                "success": False,
                "error": "当前非交易时间",
                "next_trade_time": trade_status.get("next_trade_time")
            }

        # 转换股票代码格式
        qmt_code = self._convert_stock_code(stock_code)

        # 获取行情
        quote = await qmt_client.get_stock_quote(qmt_code)
        if not quote or not quote.get("price"):
            return {"success": False, "error": f"无法获取 {stock_code} 的行情数据"}

        # 如果没有指定价格，使用跌停价快速卖出
        if not price:
            price = quote.get("limit_down", quote.get("price", 0))

        result = await qmt_client.sell_stock(
            stock_code=qmt_code,
            price=price,
            quantity=quantity,
            order_type="limit"
        )

        return {
            "success": result.get("success", True),
            "stock_code": stock_code,
            "stock_name": quote.get("stock_name", ""),
            "price": price,
            "quantity": quantity,
            "amount": price * quantity,
            "order_id": result.get("order_id"),
            "message": result.get("message", "卖出委托成功")
        }

    async def _get_quote(self, stock_code: str) -> Dict[str, Any]:
        """获取股票行情"""
        qmt_code = self._convert_stock_code(stock_code)
        quote = await qmt_client.get_stock_quote(qmt_code)

        if not quote:
            return {"success": False, "error": f"无法获取 {stock_code} 的行情数据"}

        pre_close = quote.get("pre_close", 0)
        price = quote.get("price", 0)
        change_percent = (price - pre_close) / pre_close * 100 if pre_close > 0 else 0

        return {
            "success": True,
            "stock_code": stock_code,
            "stock_name": quote.get("stock_name", ""),
            "price": price,
            "pre_close": pre_close,
            "change_percent": round(change_percent, 2),
            "open": quote.get("open", 0),
            "high": quote.get("high", 0),
            "low": quote.get("low", 0),
            "volume": quote.get("volume", 0),
            "limit_up": quote.get("limit_up", 0),
            "limit_down": quote.get("limit_down", 0)
        }

    async def _get_positions(self) -> Dict[str, Any]:
        """获取持仓列表"""
        result = await qmt_client.get_positions()
        return {
            "success": True,
            "positions": result.get("positions", []),
            "total_market_value": result.get("total_market_value", 0),
            "count": result.get("count", 0)
        }

    async def _get_balance(self) -> Dict[str, Any]:
        """获取账户资金"""
        result = await qmt_client.get_balance()
        return {
            "success": True,
            **result
        }

    def _convert_stock_code(self, stock_code: str) -> str:
        """转换股票代码格式"""
        stock_code = stock_code.strip().upper()
        if '.' in stock_code:
            return stock_code
        # 6开头是上海，0/3开头是深圳
        if stock_code.startswith('6'):
            return f"{stock_code}.SH"
        else:
            return f"{stock_code}.SZ"


# 单例
ai_trade_service = AITradeService()