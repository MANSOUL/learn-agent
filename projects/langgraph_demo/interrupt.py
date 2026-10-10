import os
import time
from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
# from langgraph.graph.message import add_messages
# from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

# load_dotenv()

# _llm = None

# def get_llm():
#     global _llm
#     if _llm is None:
#         _llm = ChatOpenAI(
#             api_key=os.getenv("OPENAI_API_KEY"),
#             base_url=os.getenv("OPENAI_BASE_URL"),
#             model=os.getenv("LLM_MODEL"),
#             temperature=0.7,
#         )
#     return _llm

class DemoState(TypedDict):
    """LangGraph Agent 的状态定义

    这是 LangGraph 最核心的概念。所有节点共享这个状态，
    节点通过读取/修改状态来协作完成任务。
    """
    current_step: int  # 当前步骤


def node1(state: DemoState) -> DemoState:
    """节点1: 读取状态，修改状态"""
    print(f"节点1: 当前步骤 {state['current_step']}")
    value = interrupt("节点1: 触发中断，等待外部输入...")
    print(f"节点1: 收到外部输入 {value}")
    state['current_step'] += value
    return state

def node2(state: DemoState) -> DemoState:
    """节点2: 读取状态，修改状态"""
    print(f"节点2: 当前步骤 {state['current_step']}")
    state['current_step'] += 1
    return state

thread_config = {"configurable": {"thread_id": 1}}

def main():
    """LangGraph Agent 的主函数"""
    graph = StateGraph(DemoState)
    graph.add_node("node1", node1)
    graph.add_node("node2", node2)
    graph.set_entry_point("node1")
    graph.add_edge("node1", "node2")
    graph.add_edge("node2", END)

    # 设置检查点保存器
    checkpointer = InMemorySaver()

    agent = graph.compile(checkpointer=checkpointer)
    initial_state = DemoState(current_step=0)
    agent.invoke(initial_state, config=thread_config)

    # 获取中断的状态
    state = agent.get_state(thread_config)
    print(f"当前状态: {state}")

    time.sleep(5)  # 等待5秒，模拟外部输入
    agent.invoke(Command(resume=2), config=thread_config)


if __name__ == "__main__":  
    main()
