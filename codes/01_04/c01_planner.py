from c00_call_llm_with_json import call_llm_with_json

def planner_execute(task: str) -> dict:
    """
    Plan-Execute 规划器：先制定完整的执行计划。

    适用场景：
      - 任务明确，不需要动态调整
      - 多个步骤之间有依赖关系
      - 需要整体把控任务进度

    Args:
        task: 用户的任务描述。

    Returns:
        包含计划步骤的字典。
    """
    system_msg = (
      "你是一个任务规划专家。请将用户的任务分解为可执行的子步骤。"
      "返回严格的 json 格式：\n"
      '{"plan": [{"step": 1, "description": "...", "tool": "工具名", rely_on: []}, ....]}\n'
      "rely_on 表示该步骤依赖的那些步骤（填写步骤号）。"
    )

    plans = call_llm_with_json(task, system_msg)

    return plans

if __name__ == "__main__":
    print(planner_execute("对比下广州和深圳的天气，然后输出一份报告"))
