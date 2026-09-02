from c01_react_agent import ReActAgent
from c02_plan_execute_agent import PlanExecuteAgent
from c03_reflexion_agent import ReflexionAgent

AGENT_REGISTRY = {
  "react": ReActAgent,
  "plan_execute": PlanExecuteAgent,
  "reflexion": ReflexionAgent
}

def run_agent_by_type(agent_type: str, task: str):
    """
    统一的 Agent 运行入口

    Args:
        agent_type: Agent 类型 react|plan_execute|reflexion
        task: 用户任务
    Returns:
        Agent执行结果
    """
    agent_class = AGENT_REGISTRY.get(agent_type)
    if agent_class is None:
        return f"不支持的 Agent 类型:{agent_type}。支持：{list(AGENT_REGISTRY.keys())}"

    print(f"\n{'='*60}")
    print(f"  Agent 类型: {agent_type.upper()}")
    print(f"  任务: {task}")
    print(f"{'='*60}")

    agent = agent_class()
    result = agent.run(task)
    print(f"\n  ✅ 最终答案:\n{result}")
    return result


if __name__ == "__main__":
    run_agent_by_type("react", "搜索关于小明的消息，然后计算8*8")
