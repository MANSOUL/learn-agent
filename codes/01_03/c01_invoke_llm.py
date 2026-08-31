import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  base_url=os.getenv("OPENAI_BASE_URL"),
)

def call_llm(prompt: str) -> str:
  """最基础的 LLM 调用 --- 发送提示词，获取恢复。
    Agent 的最底层操作：让 LLM 思考。
    后续所有 Agent 逻辑都建立在此基础之上。

    Args：
      prompt：用户输入的提示词文本。

    Returns：
      LLM 生成的回复文本。
  """
  model = os.getenv("LLM_MODEL", "gpt-5.6-terra")
  response = client.responses.create(
    model=model,
    input=prompt,
  )
  return response.output_text


print(call_llm("一句话说说 Python 是什么"))