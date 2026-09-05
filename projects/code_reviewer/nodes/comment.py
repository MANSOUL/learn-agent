from langchain_core.messages import HumanMessage, ToolMessage
# from langgraph.prebuilt import create_react_agent # old
from langchain.agents import create_agent
from state import PrReviewState
from llm_client import get_llm
from tools.github import post_pr_comment

SYSTEM_PROMPT = """你是 PR Review 团队的评论员。你的任务是:
调用 post_pr_comment 将 Review 结果评论到 issues
然后输出结果
"""

def post_comment_node(state: PrReviewState) -> PrReviewState:
    print(state["final_report"])
    llm = get_llm()
    agent = create_agent(llm, [post_pr_comment], system_prompt=SYSTEM_PROMPT)
    result = agent.invoke(
        {
            "messages": HumanMessage(
                content=f"PR URL:{state["pr_url"]}\nReview:{state["final_report"]}"
            )
        }
    )
    return state
