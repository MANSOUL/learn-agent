import json
import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from c00_tools import TOOLS, TOOL_MAP

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
)

MODEL = os.getenv("LLM_MODEL", "gpt-5.6-terra")


class ReflexionAgent:
    """
    Reflexion Agent 实现 - 反思
    """

    def __init__(self, max_reflections: int = 3):
        """
        Reflexion Agent

        Args:
            max_reflections: 最大反思迭代次数
        """
        self.max_reflections = max_reflections

    def _evaluate(self, answer: str, task: str) -> dict:
        """
        自我评估回答质量

        Args:
            answer: Ageng 回答
            task: 原始任务

        Returns:
            包含评分和问题的字典
        """
        prompt = (
          f"任务：{task}\n"
          f"回答：{answer}\n\n"
          "请从准确性、完整性、清晰度三方面评分(1-10)，"
          "并指出具体问题。返回JSON：\n"
          '{"accuracy": 0, "completeness": 0, "clarity": 0, "issues": ["问题1"]}'
        )
        response = client.responses.create(
          model=MODEL,
          input=prompt,
          text={"format": {"type": "json_object"}}
        )
        return json.loads(response.output_text)

    def run(self, task: str) -> str:
        """
        执行 反思 过程

        Args:
            task: 任务
        Returns:
            经过反思迭代优化后的最佳回答
        """

        print(f"开始任务：{task}")
        feedback_history = []

        for iteration in range(self.max_reflections):
            print(f"\n[Reflexion] 第 {iteration + 1} 轮")

            # 构建带反馈的提示词
            if feedback_history:
                feedback_text = "\n".join(
                    f"上一轮问题 {i+1}：{fb}"
                    for i, fb in enumerate(feedback_history[-1])
                )
                prompt = (
                  f"任务：{task}\n"
                  f"请改进之前的回答。之前的问题：\n{feedback_text}"
                )
                print(f"\n上一轮存在的问题：\n{feedback_text}")
            else:
                prompt = task
            
            # 执行，纯推理
            response = client.responses.create(
              model=MODEL,
              input=prompt
            )
            answer = response.output_text
            print(f"   回答：{answer[:100]}...")

            # 自我评估
            evaluation = self._evaluate(answer, task)
            avg_score = (
              evaluation.get("accuracy", 0) +
              evaluation.get("completeness", 0) +
              evaluation.get("clarity", 0)
            ) / 3
            issues = evaluation.get("issues", [])
            feedback_history.append(issues)
            print(f"   评分:{avg_score: .1f}/10 | 问题数：{len(issues)}")

            if avg_score >= 9.0:
                print(f"   质量达标，停止迭代！\n最终回答：\n{answer}")
                return answer

        return answer


if __name__ == "__main__":
    reflexion = ReflexionAgent()
    reflexion.run("这是一首简单的小情歌，唱着人民心中的快乐，我在人民广场吃着炸鸡，今夜你在哪里")
