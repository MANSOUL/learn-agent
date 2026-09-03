import json
import operator
import os
import ast
from typing import Any, Annotated, TypedDict, Literal
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

load_dotenv()


class AgentState(TypedDict):
    """LangGraph Agent 的状态定义

    这是 LangGraph 最核心的概念。所有节点共享这个状态，
    节点通过读取/修改状态来协作完成任务。

    Annotated[list, add_messages] 表示消息列表使用
    追加模式（新消息添加到末尾，不会覆盖）。
    """

    messages: Annotated[list, add_messages]
    task: str # 任务
    draft: str # 内容创作 Agent 的草稿
    review: str # 审核意见
    iteration: int # 当前迭代轮次
    approval: bool # 是否通过审核
    max_iterations: int # 最大迭代次数

WRITEER_SYSTEM_PROMPT = """你是一位专业的内容创作者。
风格要求：
    - 语言简洁有力；
    - 逻辑清晰，论据充分；
    - 面向技术读者的科普风格；
    - 字数在 300-500 字之间。
"""

REVIEWER_SYSTEM_PROMPT = """你是一位严格的内容审核编辑。
审查标准：
    - 准确性：内容是否有事实性错误？
    - 逻辑性：论述是否严密？
    - 可读性：是否通俗易懂？
    - 完整性：是否覆盖了任务要求的所有方面？

返回 JSON 格式：{"score":1-10, "issues": ["问题1", "问题2"], "approval": true|false, "suggestions": "改进意见"}
"""


def build_content_team(llm):
    """构建内容创作者团队

    Args:
        llm: LangChain ChatOpenAI的实例
    Returns:
        编译后的 LangGraph 应用
    """
    print("\n" + "=" * 60)
    print("  内容创作者团队 演示")
    print("=" * 60)

    # 定义 writer 节点函数
    def writer_node(state: AgentState) -> AgentState:
        """创作内容"""
        iteration = state.get("iteration", 0)
        review = state.get("review", "")
        draft = state.get("draft", "")
        task = state.get("task", "")

        if review and iteration > 0:
            prompt = (
              f"创作任务：{task}\n\n"
              f"上次草稿：{draft}\n\n"
              f"审核建议：{review}\n\n"
              "请根据审核建议修改操作"
            )
            print(f"[Writer] 第 {iteration} 轮修改...")
        else:
            prompt = (
              f"创作任务：{task}\n\n"
              "请根据创作任务进行创作"
            )
            print(f"[Writer] 开始创作...")

        response = llm.invoke(
            [
                ("system", WRITEER_SYSTEM_PROMPT),
                ("user", prompt),
            ]
        )
        # state["messages"].append(response)
        state["draft"] = response.content
        # state["iteration"] = state.get("iteration", 0) + 1
        return state

    # 定义 reviewer 节点
    def reviewer_node(state: AgentState) -> AgentState:
        """审核节点：审核内容"""
        print("[Reviewer] 正在审核...")

        prompt = (
          f"任务要求：{state['task']}\n\n"
          f"待审核草稿：\n{state['draft']}\n\n"
          f"请审核并评分。返回 JSON 格式。"
        )

        response = llm.invoke(
            [
                ("system", REVIEWER_SYSTEM_PROMPT),
                ("user", prompt),
            ]
        )

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            result = {"score": 5, "issues": ["无法解析审核结果"],
                       "approval": True, "suggestions": ""}

        state["review"] = result.get("suggestions", "")
        state["approval"] = result.get("approval", False)
        print(f"    评分: {result.get('score', 'N/A')}/10 | "
              f"通过: {state['approval']} | "
              f"问题: {result.get('issues', [])}")
        return state

    def should_continue(state: AgentState) -> Literal["writer", "end"]:
        """条件判断：是否需要继续修改"""
        iteration = state.get("iteration", 0)
        max_iter = state.get("max_iterations", 3)
        approval = state.get("approval", False)
        print(f"判断是否需要通过：{approval}")

        if approval:
            print(f"✅审核通过：修改了 {iteration} 次")
            return "end"

        if iteration > max_iter:
            print(f"❌达到最大迭代次数 {max_iter}，强制结束")
            return "end"

        state["iteration"] = iteration + 1
        return "writer"

    # 构建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("writer", writer_node)
    workflow.add_node("reviewer", reviewer_node)

    # 设置入口点
    workflow.set_entry_point("writer")
    # writer 走向 reviewer
    workflow.add_edge("writer", "reviewer")

    # 添加条件边：从 reviewer 根据条件走向不同分支
    workflow.add_conditional_edges(
        "reviewer", should_continue, {"writer": "writer", "end": END}
    )

    # 编译图
    app = workflow.compile()

    return app

if __name__ == "__main__":
    # 初始化 LLM
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("LLM_MODEL"),
        temperature=0.7,
    )
    team = build_content_team(llm)
    # 运行
    task = "写一篇短文介绍 AI Agent 技术对职场的影响"
    print(f"\n👤 用户: {task}")

    initial_state = {
        "messages": [HumanMessage(content=task)],
        "task": task,
        "draft": "",
        "review": "",
        "iteration": 0,
        "approval": False,
        "max_iterations": 4
    }

    final_state = team.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"📄 终稿:")
    print(f"{'='*60}")
    print(final_state["draft"])
