import json

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, ToolMessage

from state import PrReviewState
from config import ROLES, REVIEW_PROMPT
from llm_client import get_llm
from tools.github import read_file_at_pr

def make_reviewer_node(role_key: str):
    """工厂函数：用于创建 4 个 reviewer 角色的工厂函数"""
    role = ROLES[role_key]
    state_field = role["state_field"]

    def reviewer_node(state: PrReviewState) -> dict:
        system_prompt = role["system"] + "\n\n" + REVIEW_PROMPT.format(
            pr_url=state["pr_url"],
            pr_info=state["pr_info"],
            pr_diff=state["pr_diff"]
        )
        # return {"system_prompt": system_prompt}

        llm = get_llm()

        agent = create_agent(llm, [read_file_at_pr], system_prompt=system_prompt)

        result = agent.invoke(
            {"messages": [HumanMessage(content="请开始审查，只输出JSON。")]}
        )

        last = result["messages"][-1].content
        print(f"last:\n{last}")
        try:
            cleaned = re.sub(r"^```json\s*|\s*```$", "", last.strip(), flags=re.M)
            review = json.loads(cleaned)
        except Exception:
            review = {"issues": [], "summary": f"[{role['name']}] 解析失败"}
        review = json.loads(last)

        return {state_field: review}

    return reviewer_node

if __name__ == "__main__":
    mock_state = {
        "pr_url": "",
        "pr_info": "--info--",
        "pr_diff": "--diff--",
        "security_result": "",
        "performance_result": "",
        "correctness_result": "",
        "style_result": "",
        "final_report": "",
    }

    for key,value in ROLES.items():
        role_node = make_reviewer_node(key)
        print(role_node(mock_state))
