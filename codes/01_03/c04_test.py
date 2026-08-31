from c03_cycle import run_agent


TEST_CASES = [
    {
        "name": "Test 1 - 简单问答（无需工具）",
        "message": "什么是 Python 编程语言？请用一句话回答。",
        "expected_tools": 0,
    },
    {
        "name": "Test 2 - 天气查询（单工具）",
        "message": "上海今天天气怎么样？",
        "expected_tools": 1,
    },
    {
        "name": "Test 3 - 组合查询（搜索 + 计算）",
        "message": "搜索一下什么是 LangChain，然后帮我算 123 * 456 等于多少。",
        "expected_tools": 2,
    },
    {
        "name": "Test 4 - 需要推理的复杂查询",
        "message": "北京和深圳今天哪个城市更热？温度差多少？",
        "expected_tools": 2,
    },
]


def main():
    """运行所有测试用例。"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║          第1章：第一个 Agent - Hello World           ║")
    print("║          理解 Agent 循环的底层原理                    ║")
    print("╚══════════════════════════════════════════════════════╝")

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'#'*60}")
        print(f"# {test['name']}")
        print(f"# 预期工具调用数: {test['expected_tools']}")
        print(f"{'#'*60}")

        try:
            run_agent(test["message"], max_iterations=5)
        except Exception as e:
            print(f"\n❌ 运行出错: {e}")
            print("请检查 .env 文件中的 API Key 配置是否正确。")

        if i < len(TEST_CASES):
            print("\n" + "-" * 60)
            input("按 Enter 继续下一个测试...")


if __name__ == "__main__":
    main()
