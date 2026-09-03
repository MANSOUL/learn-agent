import json
import operator
import os
import ast
from typing import Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver


load_dotenv()

@tool
def get_stock_price(symbol: str) -> str:
    """查询股票实时价格。

    Args:
        symbol: 股票代码，如 AAPL（苹果）、TSLA（特斯拉）、BABA（阿里巴巴）。

    Returns:
        该股票的最新价格信息。
    """
    mock_prices = {
        "AAPL": "185.50 USD",
        "TSLA": "245.30 USD",
        "GOOGL": "175.20 USD",
        "MSFT": "420.10 USD",
        "BABA": "85.50 USD",
    }
    price = mock_prices.get(symbol.upper(), f"未找到股票 {symbol} 的数据")
    return f"{symbol.upper()}: {price} (模拟数据)"


@tool
def search_news(query: str) -> str:
    """搜索最新的新闻资讯。

    适用于获取实时新闻、事件报道、行业动态等。

    Args:
        query: 搜索关键词，如 "AI 行业动态"。

    Returns:
        相关新闻摘要。
    """
    mock_news = {
        "AI": "AI Agent 正从原型走向带评测、可观测和权限控制的工程系统。",
        "股票": "今日股市震荡，科技板块表现强劲。",
        "特斯拉": "特斯拉发布新一代自动驾驶技术，股价上涨 3%。",
    }
    for key in mock_news:
        if key in query:
            return mock_news[key]
    return f"关于 '{query}' 的新闻：行业持续发展，暂无重大事件。(模拟数据)"


@tool
def calculate_math(expression: str) -> str:
    """执行数学计算。

    Args:
        expression: 基础算术表达式，如 '100 * 1.15' 或 '(12 + 3) / 5'。

    Returns:
        计算结果。
    """
    arithmetic_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in arithmetic_operators:
            return arithmetic_operators[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in arithmetic_operators:
            return arithmetic_operators[type(node.op)](evaluate(node.operand))
        raise ValueError("只允许基础算术")

    if not expression.strip() or len(expression) > 100:
        return "计算错误：表达式为空或过长"
    try:
        return str(evaluate(ast.parse(expression, mode="eval")))
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
        return "计算错误：只允许有限长度的基础算术表达式"


def demo_langchain_agent():
    """演示 LangChain Agent 的基本用法。

    对比第1章的裸写 Agent，可以看到：
      1. 工具定义用 @tool 装饰器，更简洁
      2. Agent 执行器一行代码创建
      3. 对话历史自动管理（MemorySaver）
      4. 线程级别的对话隔离
    """
    print("\n" + "=" * 60)
    print("  LangChain Agent 演示")
    print("=" * 60)

    # 1、初始化 LLM
    llm = ChatOpenAI(
      api_key=os.getenv("OPENAI_API_KEY"),
      base_url=os.getenv("OPENAI_BASE_URL"),
      model=os.getenv("LLM_MODEL"),
      temperature=0.7
    )

    # 2、准备工具列表
    tools = [get_stock_price, search_news, calculate_math]

    # 3、创建 Agent - 内置 ReAct循环
    memory = MemorySaver() # 对话记忆管理器
    agent = create_agent(
        model=llm,
        tools=tools,
        checkpointer=memory
    )

    """
    LangChain Agent 的核心抽象：
      - LLM: ChatOpenAI —— 大脑
      - Tools: @tool 列表 —— 技能
      - Agent: create_agent —— LangChain 1.x 的高层执行器
      - Checkpointer: MemorySaver —— 记忆

    对比第1章裸写的优势：
      1. 不需要手动管理 messages 列表
      2. 不需要手动处理 tool_calls 循环
      3. 对话历史自动持久化
      4. 支持多线程（通过 thread_id 隔离对话）
    """

    # 4、运行对话
    test_queries = [
        "帮我查一下苹果(AAPL)和特斯拉(TSLA)的股价",
        "特斯拉最近有什么新闻吗？",
        "9/2等于多少",
    ]

    config = {"configurable": {"thread_id": "demo-session-1"}}

    for query in test_queries:
        print(f"\n👤 用户: {query}")

        result = agent.invoke(
            {"messages": [("user", query)]},
            config=config
        )

        # 最后一条消息是 Agent 的回复
        final_msg = result["messages"][-1]
        print(f"🤖 Agent：{final_msg.content}")

if __name__ == "__main__":
    demo_langchain_agent()
