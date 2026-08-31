import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from c02_function_calling import TOOLS,TOOL_MAP

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

def run_agent(user_message: str, max_iterations: int = 5):
    """
    简单的 ReAct Agent（循环）。

    Agent 框架（LangChain/C热舞AI/AutoGen）本质是这个循环的封装 + 增强。

    Args：
        user_message：用户输入的消息。
        max_iterations：最大工具调用轮数，防止无限循环

    Returns：
        Agent 的最终回答。
    """

    # Responses 输入项 - Agent 的短期记忆
    input_items = [
        {
            "role": "system",
            "content": "你是一个有用的 AI 助手。当需要获取最新信息或执行计算时，请使用提供的工具。",
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    print(f"\n{'='*60}")
    print(f"用户：{user_message}")
    print(f"\n{'='*60}")

    for iteration in range(max_iterations):
        # ===== 1、调用 LLM （Think 阶段） =====
        model = os.getenv("LLM_MODEL", "gpt-5.6-terra")
        response = client.responses.create(
          model = model,
          input=input_items,
          tools=TOOLS,
          tool_choice="auto"
        )

        function_calls = [
            item for item in response.output if item.type == "function_call"
        ]

        # ===== 2、检查 LLM 是否需要调用工具 =====
        if not function_calls:
            # LLM 决定直接回答（不需要工具） - 结束循环
            final_answer = response.output_text
            print(f"\n🎯 Agent 最终回答：\n${final_answer}")
            return final_answer

        # ===== 3、执行工具调用 （ACT阶段）=====
        # 保留模型输出项；下一轮需要它们与 function_call_output 对应。
        input_items.extend(response.output)

        for tool_call in function_calls:
            func_name = tool_call.name
            func_args = json.loads(tool_call.arguments)

            print(f"\n🔧 第 {iteration + 1} 轮 - 调用工具: {func_name}({func_args})")

            # 执行实际的工具函数
            tool_function = TOOL_MAP.get(func_name)
            if tool_function is None:
                result = f"错误：未找到工具{func_name}"
            else:
                result = tool_function(**func_args)

            print(f"📊 工具返回: {result}")

            # 将工具执行结果加入对话历史 (Observe阶段)
            input_items.append({
              "type": "function_call_output",
              "call_id": tool_call.call_id,
              "output": result
            })

    # 达到最大迭代次数，强制 LLM 给出最终回答
    print("\n⚠️ 达到最大迭代次数，要求 LLM 给出最终回答...")
    input_items.append({
      "role": "user",
      "content": "请基于已有的工具调用结果，给出最终答案。"
    })
    model = os.getenv("LLM_MODEL", "gpt-5.6-terra")
    final_response = client.responses.create(
      model = model,
      input=input_items,
    )
    final_answer = final_response.output_text
    print(f"\n🎯 Agent 最终回答:\n{final_answer}")
    return final_answer
