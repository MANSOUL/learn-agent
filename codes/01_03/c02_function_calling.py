TOOLS=[
    {
        "type": "function",
        "name": "get_weather",
        "description": "查询指定城市的天气信息。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 '北京'、'上海'",
                }
            },
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_web",
        "description": "搜索信息。课程中返回模拟结果，不会访问互联网。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "执行只包含基础运算符的数学计算。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '2 + 3 * 4'",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

def get_weather(city: str) -> str:
    """ 模拟天气查询。"""
    weather_data = {
        "北京": "晴天，25°C，湿度 40%，北风 3 级",
        "上海": "多云，28°C，湿度 65%，东南风 2 级",
        "深圳": "阵雨，30°C，湿度 80%，南风 4 级",
        "成都": "阴天，22°C，湿度 55%，无持续风向",
    }
    return weather_data.get(city, f"未找到 {city} 的天气数据")

def search_web(query: str) -> str:
    """模拟网络搜索。"""
    mock_results = {
        "python": "Python 是一种简洁、易读、功能强大的高级编程语言，广泛用于 Web 开发、数据分析、人工智能和自动化脚本等领域。",
        "agent": (
            "AI Agent 是一种能够自主感知环境、做出决策并执行行动的"
            "智能系统。它通常由 LLM、规划器、记忆系统和工具组成。"
        ),
        "langchain": (
            "LangChain 是一个用于构建 LLM 应用的开源框架，"
            "提供了 Agent、Chain、Tool 等核心抽象。"
        ),
    }

    for key in mock_results:
        if key in query.lower():
            return mock_results[key]
    return f"关于 '{query}' 的搜索结果：这是一个模拟结果。"

def calculate(expression: str) -> str:
    """ 安全的数学计算工具。 """
    try:
        allowed_chars = set("0123456789+-*/().%^ ")
        if not all(c in allowed_chars for c in expression):
            return "错误：表达式包含不允许的字符"
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

TOOL_MAP = {
    "get_weather": get_weather,
    "search_web": search_web,
    "calculate": calculate,
}
