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


class RoleAgent:
    """模拟 crewAI 风格的角色 Agent。

    crewAI 的核心设计理念：
      1. 每个 Agent 有明确的角色(role)、目标(goal)、背景(backstory)
      2. Agent 之间通过任务(task)来协作
      3. 可以设置 allow_delegation 允许 Agent 把任务委派给其他 Agent
    """

    def __init__(self, name: str, role: str, goal: str, backstory: str, llm):
        """初始化角色

        Args:
            name: 角色名
            role: 角色描述（如“数据分析师”）
            goal: 角色目标描述
            backstory: 角色背景故事（帮助 LLM 理解角色定位）
            llm: LangChain LLM 实例
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = llm

    def execute(self, task: str) -> str:
        """执行角色任务

        Args:
            task: 任务描述

        Returns:
            任务结果
        """
        system_prompt = (
            f"你是 {self.name}，一名 {self.role}。\n"
            f"你的目标是：{self.goal}。\n"
            f"你的背景是：{self.backstory}。\n"
        )
       
        response = self.llm.invoke([
          ("system", system_prompt),
          ("user", task)
        ])
        return response.content

def run_crew_style_demo():
    """演示 crewAI 风格的多 Agent 协作。

    场景：市场分析报告
      - 数据分析师：收集和处理数据
      - 策略规划师：基于数据制定策略
      - 报告撰写师：汇总形成最终报告
    """
    print("\n" + "=" * 60)
    print("  crewAI 风格: 市场分析团队演示")
    print("=" * 60)

    # 初始化 llm
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-5.6-terra"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=0.5,
    )

    # 创建团队
    data_analyst = RoleAgent(
        name="数据分析师",
        role="市场数据分析专家",
        goal="收集并分析市场数据，找出关键趋势和洞察",
        backstory="具有10年市场研究经验，擅长从数据中发现规律",
        llm=llm,
    )

    strategist = RoleAgent(
        name="策略规划师",
        role="商业策略专家",
        goal="基于数据洞察制定可行的商业策略",
        backstory="曾任多家顶级咨询公司顾问，擅长战略规划",
        llm=llm,
    )

    report_writer = RoleAgent(
        name="报告撰写师",
        role="专业报告撰写人",
        goal="将分析和策略整合为一份清晰、专业的研究报告",
        backstory="资深商业撰稿人，擅长将复杂信息转化为易读报告",
        llm=llm,
    )

    # 流程：数据分析 → 策略制定 → 报告撰写
    print("\n📊 阶段 1: 数据分析")
    analysis = data_analyst.execute(
        "分析2025年中国AI Agent市场的规模和主要趋势，列出3-5个关键发现"
    )
    print(f"    输出: {analysis[:150]}...")

    print("\n📈 阶段 2: 策略制定")
    strategy = strategist.execute(
        f"基于以下市场分析，制定一套市场进入策略:\n{analysis}"
    )
    print(f"    输出: {strategy[:150]}...")

    print("\n📝 阶段 3: 报告撰写")
    report = report_writer.execute(
        f"请将以下分析报告和策略建议整合为一份正式研究报告:\n\n"
        f"市场分析:\n{analysis}\n\n策略建议:\n{strategy}\n\n"
        f"要求: 结构清晰、有执行摘要、分章节、每个观点有数据支撑。"
    )
    print(f"    输出: {report[:200]}...")

    print("\n📄 ===== 最终报告摘要 =====")
    print(report if len(report) < 500 else report[:500] + "...")

run_crew_style_demo()
