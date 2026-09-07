import json
import operator
import os
import ast
from typing import Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from tools.tools_map import TOOLS 

load_dotenv()

_agent = None

def _create_my_agent():
    # 1、初始化 LLM
    llm = ChatOpenAI(
      api_key=os.getenv("OPENAI_API_KEY"),
      base_url=os.getenv("OPENAI_BASE_URL"),
      model=os.getenv("LLM_MODEL"),
      temperature=0.7
    )

    # 2、准备工具列表

    # 3、创建 Agent - 内置 ReAct循环
    system_prompt = (
        "你是一个合格的智能助手。"
        "根据用户的问题，进行回答，回答需简洁、准确。"
        "若需要使用工具，选择合适的工具，若没有合适的工具，直接回复【不知道】"
        # 友好的告诉用户你不知道这个问题。
    )
    memory = MemorySaver() # 对话记忆管理器
    agent = create_agent(
        model=llm,
        system_prompt=system_prompt,
        tools=TOOLS,
        checkpointer=memory
    )

    return agent

def _get_agent():
    global _agent
    if _agent is None:
        _agent = _create_my_agent()
    return _agent

def chat(prompt: str) -> str:
    agent = _get_agent()
    result = agent.invoke(
        {
            "messages": [
                ("user", prompt)
            ]
        },
        {"configurable": {"thread_id": "assistant-demo-session-1"}}
    )

    # 最后一条消息是 Agent 的回复
    final_msg = result["messages"][-1]
    # print(f"🤖 Agent：{final_msg.content}")
    return final_msg.content