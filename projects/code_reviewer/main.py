from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from state import PrReviewState
from nodes.supervisor import supervisor_node
from nodes.reviewer import make_reviewer_node
from nodes.aggregator import aggregator_node
from nodes.comment import post_comment_node
from llm_client import get_llm

def main():
    # 构建图
    workflow = StateGraph(PrReviewState)

    # 添加节点
    workflow.add_node("supervisor", supervisor_node)
    # security/performance/correctness/style
    workflow.add_node("security_reviewer", make_reviewer_node("security"))
    workflow.add_node("performance_reviewer", make_reviewer_node("performance"))
    workflow.add_node("correctness_reviewer", make_reviewer_node("correctness"))
    workflow.add_node("style_reviewer", make_reviewer_node("style"))
    workflow.add_node("aggregator", aggregator_node)
    workflow.add_node("post_comment", post_comment_node)

    # 添加边
    workflow.add_edge("supervisor", "security_reviewer")
    workflow.add_edge("supervisor", "performance_reviewer")
    workflow.add_edge("supervisor", "correctness_reviewer")
    workflow.add_edge("supervisor", "style_reviewer")

    workflow.add_edge("security_reviewer", "aggregator")
    workflow.add_edge("performance_reviewer", "aggregator")
    workflow.add_edge("correctness_reviewer", "aggregator")
    workflow.add_edge("style_reviewer", "aggregator")

    workflow.add_edge("aggregator", "post_comment")

    workflow.add_edge("post_comment", END)

    # 设置入口点
    workflow.set_entry_point("supervisor")

    # 添加条件边
    # workflow.add_conditional_edges(
    #     "reviewer", should_continue, {"writer": "writer", "end": END}
    # )

    # 编译图
    agent = workflow.compile()

    initial_state = {
        "pr_url": "https://github.com/MANSOUL/learn-agent/pull/1"
    }

    agent.invoke(initial_state)

main()
