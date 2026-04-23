"""
AI交易服务模块
使用OpenAI Function Calling实现自然语言交易
集成Skills系统，支持不同场景的技能激活
"""
import json
import re
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from loguru import logger

from config.settings import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from core.qmt_client import qmt_client
from services.config import SysConfigService
from services.mcp_config import mcp_config_service
from services.user import UserService
from services.trade_log import trade_log_service
from models.trade_log import TradeActionType
from skills import skill_service
from models.user import User


async def get_ai_config(key: str, default: str = "") -> str:
    """从数据库获取AI配置"""
    service = SysConfigService()
    value = await service.get_config_value(key)
    return value if value else default


async def get_user_qmt_api_key(user: User) -> Optional[str]:
    """获取用户的 QMT API Key"""
    user_service = UserService()
    qmt_config = await user_service.get_qmt_account(user.id)
    return qmt_config.get("qmt_api_key") if qmt_config else None


async def check_user_qmt_permission(user: User) -> tuple[bool, str]:
    """
    检查用户是否有 QMT 交易权限

    Returns:
        tuple[bool, str]: (是否有权限, 错误消息)
    """
    if not user:
        return False, "请先登录"

    # 检查角色权限
    if user.role not in ["admin", "trader"]:
        return False, "您没有交易权限，请联系管理员开通 trader 或 admin 角色"

    # 检查 QMT 账户是否绑定
    if not user.qmt_account_id:
        return False, "请先绑定 QMT 账户"

    # 检查 QMT 是否启用
    if not user.qmt_enabled:
        return False, "QMT 交易未启用，请在用户设置中开启"

    return True, ""


class AITradeService:
    """AI交易服务"""

    def __init__(self):
        self.client = None
        self.model = OPENAI_MODEL
        # 初始化Skills服务
        skill_service.discover_skills()

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
                                "description": "卖出数量（股），可以是任意数量"
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
            },
            {
                "type": "function",
                "function": {
                    "name": "bind_qmt_account",
                    "description": "绑定QMT交易账户。当用户需要交易但尚未绑定账户时调用此函数。",
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
- 买入数量必须是100的整数倍（A股规则）
- 卖出数量没有限制，可以卖出任意数量（包括零头）
- 交易时间：工作日9:30-11:30, 13:00-15:00
- 如果用户没有指定价格，买入默认使用涨停价（快速成交），卖出使用跌停价
- 股票代码6开头是上海，0/3开头是深圳

请用简洁的中文回复。"""

    async def chat(self, message: str, context: Dict[str, Any] = None, user: User = None) -> Dict[str, Any]:
        """
        处理用户消息

        Args:
            message: 用户消息
            context: 上下文信息（持仓、资金等）
            user: 当前用户（用于权限校验）

        Returns:
            AI响应结果
        """
        try:
            # 初始化客户端
            if not self.client:
                await self._init_client()

            # 设置用户的 QMT API Key
            if user:
                qmt_api_key = await get_user_qmt_api_key(user)
                if qmt_api_key:
                    qmt_client.set_api_key(qmt_api_key)
                else:
                    # 尝试从 MCP 配置获取
                    mcp_config = await mcp_config_service.get_config_value("qmt-service")
                    if mcp_config and mcp_config.get("api_key"):
                        qmt_client.set_api_key(mcp_config["api_key"])

            # 检测匹配的Skill
            matched_skill = skill_service.match_skill(message)

            # 获取系统提示词和工具
            if matched_skill:
                system_prompt = matched_skill.get_system_prompt()
                tools = matched_skill.get_tools(self.tools)
                skill_name = matched_skill.name
                logger.info(f"激活Skill: {skill_name}")
            else:
                system_prompt = self.system_prompt
                tools = self.tools
                skill_name = None

            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt}
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
                tools=tools,
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

                    # 执行函数（带权限校验）
                    result = await self._execute_function_with_permission(function_name, function_args, user)
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
                    messages=messages,
                    tools=tools,
                    tool_choice="none"  # 防止再次调用工具
                )

                return {
                    "role": "assistant",
                    "content": final_response.choices[0].message.content,
                    "function_called": function_name if len(assistant_message.tool_calls) == 1 else None,
                    "function_result": tool_results[0]["content"] if len(tool_results) == 1 else None,
                    "skill": skill_name
                }

            # 检查是否是纯文本工具调用（某些模型不支持 function calling）
            content = assistant_message.content or ""
            parsed_tool_call = self._parse_text_tool_call(content)
            if parsed_tool_call:
                function_name = parsed_tool_call["name"]
                function_args = parsed_tool_call["parameters"]

                # 执行函数（带权限校验）
                result = await self._execute_function_with_permission(function_name, function_args, user)

                # 将结果发送给 AI 生成最终回复
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": f"函数 {function_name} 的执行结果：{json.dumps(result, ensure_ascii=False)}\n请根据结果生成回复。"
                })

                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="none"
                )

                return {
                    "role": "assistant",
                    "content": final_response.choices[0].message.content,
                    "function_called": function_name,
                    "function_result": json.dumps(result, ensure_ascii=False),
                    "skill": skill_name
                }

            return {
                "role": "assistant",
                "content": content or "抱歉，我没有理解您的请求。",
                "skill": skill_name
            }

        except Exception as e:
            logger.error(f"AI聊天失败: {e}")
            return {
                "role": "assistant",
                "content": f"抱歉，处理您的请求时出现错误：{str(e)}"
            }

    def _parse_text_tool_call(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析纯文本工具调用 JSON

        某些模型返回的格式是 {"name": "xxx", "parameters": {...}}
        而不是标准的 OpenAI function calling 格式

        Args:
            content: AI 返回的文本内容

        Returns:
            解析后的工具调用，如果不是工具调用则返回 None
        """
        # 尝试匹配 JSON 格式的工具调用
        patterns = [
            r'\{["\']?\s*name\s*["\']?\s*:\s*["\'](\w+)["\'],\s*["\']?\s*parameters\s*["\']?\s*:\s*(\{[^}]+\})\s*\}',
            r'\{["\']?\s*name\s*["\']?\s*:\s*["\'](\w+)["\']\s*,\s*["\']?\s*parameters\s*["\']?\s*:\s*\{[^}]*["\']?\s*stock_code\s*["\']?\s*:\s*["\']([^"\']+)["\'][^}]*\}\s*\}'
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    # 尝试解析整个 JSON
                    json_match = re.search(r'\{[^{}]*\}', content)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        if "name" in parsed and "parameters" in parsed:
                            return parsed
                except json.JSONDecodeError:
                    pass

        return None

    async def _execute_function_with_permission(
        self,
        function_name: str,
        args: Dict[str, Any],
        user: User = None
    ) -> Dict[str, Any]:
        """
        执行函数调用（带权限校验）

        Args:
            function_name: 函数名称
            args: 函数参数
            user: 当前用户

        Returns:
            执行结果
        """
        # 交易相关函数需要权限校验（已包含用户 qmt_enabled 检查）
        trade_functions = ["buy_stock", "sell_stock"]

        if function_name in trade_functions:
            if not user:
                return {"success": False, "error": "请先登录"}

            has_permission, error_msg = await check_user_qmt_permission(user)
            if not has_permission:
                return {"success": False, "error": error_msg}

        return await self._execute_function(function_name, args, user)

    async def _execute_function(self, function_name: str, args: Dict[str, Any], user: User = None) -> Dict[str, Any]:
        """执行函数调用"""
        try:
            if function_name == "buy_stock":
                return await self._buy_stock(
                    args.get("stock_code"),
                    int(args.get("quantity", 0)),
                    float(args.get("price", 0)) if args.get("price") else None,
                    user
                )

            elif function_name == "sell_stock":
                return await self._sell_stock(
                    args.get("stock_code"),
                    int(args.get("quantity", 0)),
                    float(args.get("price", 0)) if args.get("price") else None,
                    user
                )

            elif function_name == "get_quote":
                return await self._get_quote(args.get("stock_code"))

            elif function_name == "get_positions":
                return await self._get_positions()

            elif function_name == "get_balance":
                return await self._get_balance()

            elif function_name == "bind_qmt_account":
                return {"success": False, "error": "请先在用户设置页面绑定QMT账户并开启交易功能", "action": "bind_qmt_account"}

            else:
                return {"success": False, "error": f"未知函数: {function_name}"}

        except Exception as e:
            logger.error(f"执行函数失败: {function_name}, {e}")
            return {"success": False, "error": str(e)}

    async def _buy_stock(self, stock_code: str, quantity: int, price: float = None, user: User = None) -> Dict[str, Any]:
        """买入股票"""
        # 检查交易时间
        try:
            trade_status = await qmt_client.get_trade_status()
        except Exception as e:
            return {"success": False, "error": "QMT未连接，请先启动QMT客户端并登录账号"}

        if not trade_status.get("is_trade_time"):
            return {
                "success": False,
                "error": "当前非交易时间",
                "next_trade_time": trade_status.get("next_trade_time")
            }

        # 转换股票代码格式（支持股票名称）
        qmt_code = await self._convert_stock_code(stock_code)

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

        success = result.get("success", True)

        # 记录交易日志
        await trade_log_service.log_action(
            action_type=TradeActionType.BUY,
            action_name="AI买入",
            action_source="ai",
            stock_code=stock_code,
            stock_name=quote.get("stock_name", ""),
            order_id=result.get("order_id"),
            action_data={"price": price, "quantity": quantity, "qmt_code": qmt_code},
            result="success" if success else "failed",
            result_message=result.get("message", "买入委托成功") if success else None,
            error_message=result.get("error") if not success else None,
            user_id=user.id if user else None,
            user_name=user.username if user else None,
            remark="通过AI交易助手下单"
        )

        return {
            "success": success,
            "stock_code": stock_code,
            "stock_name": quote.get("stock_name", ""),
            "price": price,
            "quantity": quantity,
            "amount": price * quantity,
            "order_id": result.get("order_id"),
            "message": result.get("message", "买入委托成功")
        }

    async def _sell_stock(self, stock_code: str, quantity: int, price: float = None, user: User = None) -> Dict[str, Any]:
        """卖出股票"""
        # 检查交易时间
        try:
            trade_status = await qmt_client.get_trade_status()
        except Exception as e:
            return {"success": False, "error": "QMT未连接，请先启动QMT客户端并登录账号"}

        if not trade_status.get("is_trade_time"):
            return {
                "success": False,
                "error": "当前非交易时间",
                "next_trade_time": trade_status.get("next_trade_time")
            }

        # 转换股票代码格式（支持股票名称）
        qmt_code = await self._convert_stock_code(stock_code)

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

        success = result.get("success", True)

        # 记录交易日志
        await trade_log_service.log_action(
            action_type=TradeActionType.SELL,
            action_name="AI卖出",
            action_source="ai",
            stock_code=stock_code,
            stock_name=quote.get("stock_name", ""),
            order_id=result.get("order_id"),
            action_data={"price": price, "quantity": quantity, "qmt_code": qmt_code},
            result="success" if success else "failed",
            result_message=result.get("message", "卖出委托成功") if success else None,
            error_message=result.get("error") if not success else None,
            user_id=user.id if user else None,
            user_name=user.username if user else None,
            remark="通过AI交易助手下单"
        )

        return {
            "success": success,
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
        qmt_code = await self._convert_stock_code(stock_code)
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

    async def _convert_stock_code(self, stock_code: str) -> str:
        """转换股票代码格式，支持股票名称查询"""
        stock_code = stock_code.strip()

        # 如果已经包含后缀，直接返回
        if '.' in stock_code:
            return stock_code.upper()

        # 如果是纯数字代码，添加后缀
        if stock_code.isdigit():
            code = stock_code.upper()
            # 6开头是上海，0/3开头是深圳
            if code.startswith('6'):
                return f"{code}.SH"
            else:
                return f"{code}.SZ"

        # 如果是股票名称，需要搜索获取代码
        try:
            import json
            from pathlib import Path

            stock_file = Path(__file__).parent.parent / "data" / "stocks.json"
            if stock_file.exists():
                with open(stock_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                stocks = data.get("stocks", [])
                keyword = stock_code.upper()

                for stock in stocks:
                    code = stock.get("code", "")
                    name = stock.get("name", "")

                    # 匹配股票名称
                    if keyword in name.upper() or name.upper() in keyword:
                        # 添加后缀
                        if code.startswith('6'):
                            return f"{code}.SH"
                        else:
                            return f"{code}.SZ"
        except Exception as e:
            logger.warning(f"搜索股票名称失败: {e}")

        # 如果找不到，返回原始输入（后面会报错）
        return stock_code.upper()


# 单例
ai_trade_service = AITradeService()