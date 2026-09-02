import json
import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from c00_tools import TOOLS,TOOL_MAP

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), 
    base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("LLM_MODEL", "gpt-5.6-terra")

class ReActAgent:
    """
    ReAct Agent 实现 - 最经典的 Agent 模式
    """

    def __init__(self, system_prompt: Optional[str] = None):
        """
        初始化ReAct Agent

        Args:
            system_prompt: 自定义系统提示词
        """
        self.system_prompt = system_prompt or (
            "你是一个厉害的助手。面对需要实时信息或计算时，请使用提供的工具，推理请在思考后行动。"
        )

    def run(self, user_message: str, max_steps: int = 5) -> str:
        """
        运行

        Args:
            user_message: 用户消息
            max_steps: 最大循环次数

        Returns:
            Agent 的最终答案
        """

        input_items = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        for step in range(max_steps):
            print(f"\nReAct 第{step + 1}次循环")
            response = client.responses.create(
                model=MODEL, input=input_items, tools=TOOLS, tool_choice="auto"
            )
            tool_calls = [
                item for item in response.output if item.type == "function_call"
            ]
            if not tool_calls:
                print(f"\n获取到最终答案:{response.output_text}")
                return response.output_text

            for tool in tool_calls:
                tool_name = tool.name
                tool_args = json.loads(tool.arguments)
                print(f"\n调用工具:{tool.name},参数 {tool_args}")
                result = TOOL_MAP[tool_name](**tool_args)
                print(f"\n工具结果:{result}")
                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool.call_id,
                        "output": result,
                    }
                )
        print(f"\n达到最大限定步数，无法完成任务")
        return "达到最大限定步数，无法完成任务"


if __name__ == "__main__":
    reAct = ReActAgent()
    reAct.run("搜索关于小明的消息，然后计算8*8")
