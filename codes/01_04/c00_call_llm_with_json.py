import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
  base_url=os.getenv("OPENAI_BASE_URL")
)

def call_llm_with_json(prompt: str, system_msg: str = "") -> dict:
    """
    通过 Responses API 请求 JSON 对象。

    在 Agent 开发中，经常需要 LLM 返回结构化数据
    （如规划步骤、实体提取结果等）。

    Args:
        prompt: 用户提示词。
        system_msg: 系统消息（可选）。

    Returns:
        LLM 返回的 JSON 字典。
    """
    model = os.getenv("LLM_MODEL", "gpt-5.6-terra")
    reponse = client.responses.create(
      model=model,
      input=prompt,
      instructions=system_msg or None,
      text={"format": {"type": "json_object"}}
    )
    return json.loads(reponse.output_text)

if __name__ == "__main__":
    prompt = "小明今年18岁，他喜欢吃汉堡"
    system_msg = (
        "你是一个人物画像师，"
        "请严格按照如下json格式返回人物信息："
        '{"name": "姓名", "age": "年龄", "sex": "性别"}'
    )
    print(call_llm_with_json(prompt, system_msg))
