from c04_run_agent_by_type import run_agent_by_type

if __name__ == "__main__":
    test_task = "分析 Python 和 JavaScript 各自的优势，给出学习建议。"

    print("\n▶ 3.1 测试 ReAct Agent")
    result = run_agent_by_type("react", test_task)
    print(f"ReAct Agent结果 {result}")

    print("\n▶ 3.2 测试 Plan-Execute Agent")
    result = run_agent_by_type("plan_execute", test_task)
    print(f"Plan-Execute Agent结果 {result}")

    print("\n▶ 3.3 测试 Reflexion Agent")
    result = run_agent_by_type("reflexion", test_task)
    print(f"Reflexion Agent结果 {result}")
