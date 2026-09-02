import json
import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from c00_tools import TOOLS, TOOL_MAP

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("LLM_MODEL", "gpt-5.6-terra")


class PlanExecuteAgent:
    """
    ReAct Agent 实现 - 最经典的 Agent 模式
    """

    def __init__(self, system_prompt: Optional[str] = None):
        """
        初始化ReAct Agent

        Args:
            system_prompt: 自定义系统提示词
        """
        self.plan = []
        self.result = {}
        self.system_prompt = system_prompt or (
            "你是一个任务规划专家。需要为用户的需求做好整体规划，制定详细计划，规划好计划中的每个步骤，"
            "数据仅返回严格的JSON："
            '{"plan": [{"step": 1, description: "步骤描述", "tool_name": "使用的工具名", "tool_args": {}, "rely_on": [2,3]},...]}\n'
            "step 表示步骤序号，rely_on 表示当前步骤所依赖的步骤序列号，工具所需参数，tool_args 表示工具所需的参数返回 JSON 格式"
        )

    def make_plan(self, user_message: str):
        """
        运行

        Args:
            user_message: 用户消息
            max_steps: 最大循环次数

        Returns:
            Agent 的最终答案
        """
        print("制定任务计划")
        input_items = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        response = client.responses.create(
            model=MODEL, 
            input=input_items, 
            tools=TOOLS, 
            tool_choice="auto",
            text={"format": {"type": "json_object"}}
        )

        print(f"\n制定的计划如下:\n{response.output_text}")
        data = json.loads(response.output_text)
        self.plan = data.get("plan")

    def run(self, task: str) -> str:
        """
        制定计划并执行

        Args:
            task: 任务
        Returns:
            任务结果
        """

        # 1、制定计划
        self.make_plan(task)

        # 2、执行计划
        print("\n执行计划")

        for step in self.plan:
            print(f"\n执行计划 {step.get("step")}")
            tool_name = step.get("tool_name", "none")
            tool_args = step.get("tool_args")
            if tool_name == "none":
                result = f"已完成：{step.get("description")}"
            elif tool_name in TOOL_MAP:
                result = TOOL_MAP[tool_name](**tool_args)
            else:
                result = f"暂不支持的工具：{tool_name}"
            print(f"\n计划{step.get("step")}的结果：{result}")
            self.result[f"step_{step.get("step")}"] = result

        # 3、汇总，生成最终答案
        print("\n开始汇总结果，生成最终答案")
        summary = (
          f"任务：{task}\n"
          f"执行结果：\n{json.dumps(self.result, ensure_ascii=False)}"
          "请基于以上结果给出最终答案"
        )
        response = client.responses.create(
          model=MODEL,
          input=summary
        )
        print(f"\n最终答案：\n{response.output_text}")
        return response.output_text


if __name__ == "__main__":
    reAct = PlanExecuteAgent()
    reAct.run("搜索关于小明的消息，然后计算8*8")
