import json
import operator
import os
import ast
from typing import Any, Annotated, TypedDict
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
    task_result: str
    step_count: int

def demo_langgraph_agent():
    """演示 LangGraph Agent 的基本用法。

    实现一个简单的分析流程：
        输入问题  》 LLM分析 》 判断是否需要工具 》 输出结论
    
    LangGraph 让我们可以自定义 Agent 的执行图结构，
    而不是拘泥于固定的 ReAct 循环。
    """
    print("\n" + "=" * 60)
    print("  LangGraph 状态机 Agent 演示")
    print("=" * 60)

    # 初始化 LLM
    llm = ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("LLM_MODEL"),
        temperature=0.7,
    )

    # 定义节点函数
    def analyze_node(state: AgentState) -> AgentState:
        """分析节点：让 LLM 理解用户输入。"""
        print("[Node:analyze] 正在分析用户输入...")
        response = llm.invoke([
            ("system", "分析用户问题，提取关键信息。简洁回答。"),
            ("user", state["messages"][-1].content)
        ])
        state["messages"].append(response)
        state["task_result"] = response.content
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    def should_continue(state: AgentState) -> AgentState:
        """条件判断：是否需要进一步处理？"""
        result = state["task_result"]
        if len(result) < 50:
            print("[Edge] 回答太短，需要补充详细分析")
            return "elaborate"
        print("[Edge] 回答充分，结束流程")
        return "end"

    def elaborate_node(sate: AgentState) -> AgentState:
        """扩展节点：补充详细分析"""
        print("[Node:elaborate] 正在补充详细分析...")
        response = llm.invoke([
            ("system", "请更详细地展开分析，提供更多上下文和细节"),
            ("user", state["task_result"])
        ])
        state["messages"].append(response)
        state["task_result"] = response.content
        state["step_count"] = state.get("step_count", 0) + 1
        return state

    # 构建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("elaborate", elaborate_node)

    # 设置入口点
    workflow.set_entry_point("analyze")

    # 添加条件边：从 analyze 根据条件走向不同分支
    workflow.add_conditional_edges(
        "analyze",
        should_continue,
        {
            "elaborate": "elaborate",
            "end": END
        }
    )

    # elaborate 完成后结束
    workflow.add_edge("elaborate", END)

    # 编译图
    app = workflow.compile()

    """
    图结构示意：

      [START]
         │
         ▼
    ┌──────────┐     条件判断      ┌───────────┐
    │  analyze  ├──────────────────→│ elaborate  │
    └─────┬─────┘  (太短)          └─────┬─────┘
          │ (足够)                       │
          ▼                              ▼
       [END]                          [END]

    这就是 LangGraph 的核心优势：
    用代码定义复杂的执行流程，而非硬编码在循环中。
    """

    # 运行
    test_input = "LangGraph 是什么？请简短说明。"
    print(f"\n👤 用户: {test_input}")

    initial_state = {
        "messages": [HumanMessage(content=test_input)],
        "task_result": "",
        "step_count": 0,
    }

    final_state = app.invoke(initial_state)
    print(f"\n🤖 Agent: {final_state['task_result']}")
    print(f"   总步骤数: {final_state['step_count']}")

if __name__ == "__main__":
    demo_langgraph_agent()
