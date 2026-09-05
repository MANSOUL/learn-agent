from langchain_core.messages import HumanMessage, ToolMessage
# from langgraph.prebuilt import create_react_agent # old
from langchain.agents import create_agent
from state import PrReviewState
from llm_client import get_llm
from tools.github import get_pr_info, get_pr_diff

SUPERVISOR_SYSTEM = """你是 PR Review 团队的主管。你的任务是:
1. 调用 get_pr_info 获取 PR 元数据
2. 调用 get_pr_diff 获取变更 diff

不要做审查工作。"""

def supervisor_node(state: PrReviewState) -> PrReviewState:
    llm = get_llm()
    agent = create_agent(
        llm, [get_pr_info, get_pr_diff], system_prompt=SUPERVISOR_SYSTEM
    )
    result = agent.invoke({
      "messages": HumanMessage(content=f"通过给你的PR URL，获取这个 PR 的信息和 diff: {state["pr_url"]}")
    })

    # 从消息历史中提取工具结束
    pr_info, pr_diff = "", ""
    for msg in result["messages"]:
        # msg.pretty_print()
        if isinstance(msg, ToolMessage):
            c = msg.content
            if msg.name == "get_pr_info":
                pr_info = c
            elif msg.name == "get_pr_diff":
                pr_diff = c

    # print(f"pr_info:\n{pr_info}")
    # print(f"pr_diff:\n{pr_diff}")
    state["pr_info"] = pr_info
    state["pr_diff"] = pr_diff

    return state
