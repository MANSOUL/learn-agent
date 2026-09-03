import json
import time
from typing import Callable

class AgentEvaluator:

    def __init__(self, llm: Callable = None):
        self.llm = llm
        self.results = []

    def evaluate(self, agent_func: Callable, test_cases: list[dict]) -> list[dict]:
        # 执行结果
        self.results = []

        # 执行测试用例
        for i, case in enumerate(test_cases):
            # 记录用例开始时间
            start_time = time.time()
            try:
                # 执行 agent 工具
                output = agent_func(case["input"])
                error = None
            except Exception as e:
                output = ""
                error = str(e)

            # 耗时
            elapsed = time.time() - start_time

            score = 1.0
            details = []

            # 检查关键词
            if "expected_keywords" in case and case["expected_keywords"]:
                keyword_score = self._check_keywords(
                    output, case["expected_keywords"]
                )
                score *= keyword_score
                details.append(f"关键词匹配：{keyword_score: .2f}")

            # 没有输出或输出太短 分数减半
            if not output or len(output) < 10:
                score *= 0.5
                details.append("输出过短")

            # 检查是否有错误，有错误直接0分
            if error:
                score *= 0
                details.append(f"执行错误：{error}")

            weight = case.get("weight", 1.0)
            result = {
              "case_id": i + 1,
              "input": case["input"],
              "output": output[:200],
              "score": score,
              "weight": weight,
              "error": error,
              "elapsed_sec": round(elapsed, 2),
              "details": details
            }
            self.results.append(result)
            print(f"    评分：{score: .2f} | 耗时：{elapsed: .2f}s")

        return self.results

    def _check_keywords(self, output: str, keywords: list[str]) -> float:
        # 没有 期望的关键词 列表，默认全部匹配
        if not keywords:
            return 1.0
        # 匹配上的关键词数量 / 关键词总和
        matched = sum(1 for kw in keywords if kw.lower() in output.lower())
        return matched / len(keywords)

    def summary(self) -> str:

        if not self.results:
            return "无评测结果。"

        total_weight = sum(r["weight"] for r in self.results)
        weighted_score = sum(
          r["score"] * r["weight"] for r in self.results
        ) / total_weight if total_weight > 0 else 0

        passed = sum(1 for r in self.results if r["score"] >= 0.7)
        failed = len(self.results) - passed

        lines = [
            "=" * 55,
            "  📊 Agent 评测报告",
            "=" * 55,
            f"  总用例数: {len(self.resuglts)}",
            f"  通过 (≥0.7): {passed}",
            f"  失败 (<0.7): {failed}",
            f"  加权平均分: {weighted_score:.2f}",
            f"  平均耗时: {sum(r['elapsed_sec'] for r in self.results) / len(self.results):.2f}s",
            "-" * 55,
        ]

        for r in self.results:
            status = "✅" if r["score"] >= 0.7 else "❌"
            lines.append(
                f"  {status} Case {r['case_id']}: "
                f"score={r['score']:.2f} | time={r['elapsed_sec']}s"
            )
            if r["details"]:
                for d in r["details"]:
                    lines.append(f"     └─ {d}")

        lines.append("=" * 55)
        return "\n".join(lines)


def demo_evaluation():
    """演示 Agent 评测体系。"""
    print("\n" + "=" * 60)
    print("  Agent 评测体系演示")
    print("=" * 60)

    # 模拟一个「简单 Agent」
    def mock_agent(user_input: str) -> str:
        """模拟 Agent —— 用于演示评测流程。"""
        if "天气" in user_input:
            return "当前天气晴好，气温25°C，湿度适中，适合户外活动。"
        if "计算" in user_input:
            try:
                expr = user_input.split("计算")[-1].strip()
                return f"计算结果为: {eval(expr)}"
            except Exception:
                return "计算失败，请检查表达式。"
        if "搜索" in user_input:
            return "搜索结果: 找到了相关信息，详情请查看链接。"
        return "我不太理解您的问题，请提供更多信息。"

    # 准备测试用例
    test_cases = [
        {
            "input": "北京今天天气怎么样？",
            "expected_keywords": ["天气", "温度", "°C"],
            "weight": 1.0,
        },
        {
            "input": "帮我算计算123 + 456",
            "expected_keywords": ["579", "计算结果"],
            "weight": 1.0,
        },
        {
            "input": "搜索 Python 教程",
            "expected_keywords": ["搜索", "结果"],
            "weight": 0.5,
        },
        {
            "input": "写一首关于春天的诗",
            "expected_keywords": ["春"],
            "weight": 1.5,
        },
    ]

    evaluator = AgentEvaluator()
    evaluator.evaluate(mock_agent, test_cases)
    print("\n" + evaluator.summary())

demo_evaluation()