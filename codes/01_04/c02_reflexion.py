from c00_call_llm_with_json import call_llm_with_json

def reflexion_review(original_answer: str, criteria: str) -> dict:
    """
    Reflexion 反思器：对已有的回答进行自我批评和改进。

    核心思想：
      Agent 完成一个动作后，让 LLM 自己审视结果：
      - 哪里做得好？
      - 哪里有不足？
      - 下次应该怎么改进？

    类比：像学生做了一道题后，自己用红笔批改并写反思。

    Args:
        original_answer: Agent 的原始输出。
        criteria: 评估标准。

    Returns:
        包含反思结果的字典。
    """
    system_msg = (
      "你是一个严格的质量审查员。请审查以下回答，"
      "指出问题和改进建议。返回严格的 JSON 格式：\n"
      '{"score": 1-10, "issues": ["问题1", "问题2"], "improved_answer": "改进后的回答"}'
    )
    prompt = (
      f"原始回答：\n{original_answer}\n\n"
      f"评估标准：\n{criteria}\n\n"
      f"请评估并改进。"
    )

    return call_llm_with_json(prompt, system_msg)

if __name__ == "__main__":
    print(reflexion_review("18岁男小明", "语句需通顺"))