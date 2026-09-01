from c01_planner import planner_execute
from c02_reflexion import reflexion_review
from c03_memory import AgentMemory

def run_full_demo():

    # 初始化记忆系统
    memory = AgentMemory(max_short_term=5)

    # 当前的任务
    task = "调查广州和深圳的天气，然后写一份简短的对比报告"
    print("📋 任务: {task}")

    # 1、指定计划：调用 规划器 指定完整的计划
    print("\n--- 阶段 1: 规划器制定计划 ---")
    plan = planner_execute(task)
    print(f"规划了 {len(plan['plan'])} 个步骤：\n")
    for step in plan["plan"]:
        deps = f"（{step['rely_on']}）" if step["rely_on"] else ""
        print(f"步骤 {step['step']}: {step['description']} 依赖步骤 {deps}")
        memory.set_working(f"step_{step['step']}", step["description"])

    # 2、调用工具
    print("\n--- 阶段 2: 工具调用（模拟）---")
    weather_data = {
        "广州": "晴天 25°C 湿度40%",
        "深圳": "多云 28°C 湿度65%",
    }
    for city in ["广州", "深圳"]:
        result = weather_data[city]
        memory.set_working(f"weather_{city}", result)
        print(f"  get_weather({city}) → {result}")

    # 3：生成回答
    print("\n--- 阶段 3: 生成对比报告（模拟）---")
    guangzhou = memory.get_working("weather_广州")
    shenzhen = memory.get_working("weather_深圳")
    answer = f"广州天气：{guangzhou}\n深圳天气：{shenzhen}\n建议：深圳温度更高且湿度大，"
    answer += "广州更适合户外活动。"
    print(f"  初版回答:\n{answer}")

    # 4：反思
    print("\n--- 阶段 4: 反思器自我审查 ---")
    review = reflexion_review(
        answer, "应包含数值对比（温度差、湿度差）和明确的活动建议"
    )
    print(f"  评分: {review['score']}/10")
    print(f"  问题: {review['issues']}")
    print(f"\n  改进后回答:\n{review['improved_answer']}")

    memory.add_conversation_to_short_term(task, review["improved_answer"])

    # 展示记忆状态
    print("\n--- 记忆系统状态 ---")
    print(memory.get_context_for_llm())

run_full_demo()
