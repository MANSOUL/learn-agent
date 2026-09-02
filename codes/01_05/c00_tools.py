import ast
import operator

# 共享工具集
TOOLS = [
    {
        "type": "function",
        "name": "search",
        "description": "返回课程内置的模拟搜索结果；不访问互联网。",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "搜索关键词"}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculator",
        "description": "执行只含基础运算符的数学表达式。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "数学表达式"}
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculate_safely(expression: str) -> str:
    """解释一个受限算术 AST，拒绝名称、调用和属性访问。"""
    if len(expression) > 100:
        return "表达式过长"

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in {int, float}:
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](evaluate(node.operand))
        raise ValueError("只允许基础算术")

    try:
        return str(evaluate(ast.parse(expression, mode="eval")))
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
        return "表达式错误"


TOOL_MAP = {
    "search": lambda query: f"搜索结果(模拟): 关于'{query}'的信息...",
    "calculator": lambda expression: f"计算结果: {calculate_safely(expression)}",
}
